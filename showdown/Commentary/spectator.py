import constants
import asyncio
import logging
from showdown.websocket_client import PSWebsocketClient
from showdown.Commentary.LLMCommentator import LLMCommentator
from showdown.Commentary.parsingUtils import chunk_message_smartly
from showdown.Commentary.constants import *

MAX_MESSAGE_LENGTH = 300  # Arbitrary limit, adjust based on Pokémon Showdown's exact message limit
MESSAGE_DELAY = .25  # Delay in seconds between messages
WAIT_FOR_MOVE_DELAY = 5  # Delay in seconds to wait for players to make a move

class Spectator:
	def __init__(self, num_max_connections=1):
		self.num_max_connections = num_max_connections
		self.connection_semaphore = asyncio.Semaphore(num_max_connections)
		self.curr_connections = 0
		self.logger = logging.getLogger(__name__)
		self.llm_commentator = LLMCommentator()

	async def spectate_and_read_logs(self, ps_websocket_client: PSWebsocketClient):
		"""
		This method attempts to spectate a random room and read logs from it, 
		ensuring the number of connections is within the allowed limit.
		"""
		async with self.connection_semaphore:
			# Increment current connections if successfully joined
			room_name = await ps_websocket_client.join_random_room_as_spectator()
			if room_name:
				self.curr_connections += 1
				self.logger.info(f"Joined room successfully. Current connections: {self.curr_connections}")
				self.periodically_send_disclosure(ps_websocket_client)
				# Read logs from the battle
				await self.read_logs_from_battle(ps_websocket_client, room_name)
				await ps_websocket_client.leave_battle(room_name)
			else:
				self.logger.error("Failed to join room.")

	async def read_logs_from_battle(self, ps_websocket_client: PSWebsocketClient, room_name: str):
		"""
		This method listens to the websocket and reads the battle logs, ensuring the logs are written
		to a file until the battle ends.
		"""
		global MAX_MESSAGE_LENGTH, MESSAGE_DELAY, WAIT_FOR_MOVE_DELAY
		print("Reading logs from battle")
		battle_has_started = False
		# f = open("readLogs.txt", "w")

		with open("commentaryLogs.txt", "a") as f:
			try:
				while True:
					try:
						msg = await ps_websocket_client.receive_message()
					except Exception as e:
						self.logger.error(f"Error receiving message: {e}")
						continue
					
					if self.stop_command_present(msg):
						self.logger.info("Stop command detected. Leaving battle.")
						break

					if not battle_has_started:
						if "|start" in msg:
							battle_has_started = True
						else:
							continue
					
					if "|turn" not in msg:
						await asyncio.sleep(WAIT_FOR_MOVE_DELAY)  # Wait for players to make a decision
						continue
					
					commentary = self.llm_commentator.get_commentary(msg)
					commentary_content = commentary.content

					# self.logger.debug(commentary_content)
					commentary_chunks = chunk_message_smartly(MAX_MESSAGE_LENGTH, commentary_content)
					for chunk in commentary_chunks:
						await ps_websocket_client.send_message(room_name, [chunk])
						# f.write(f"{chunk}\n")
						# self.logger.debug(f"Sent commentary chunk: {chunk}")
						await asyncio.sleep(MESSAGE_DELAY)  # Throttle message sending to avoid rate limits

					# self.logger.debug(commentary)
					# self.logger.debug(msg)

					# Check for battle start or end strings
					if constants.WIN_STRING in msg:
						self.logger.info("Battle end detected")
						break
					else:
						# Additional logging to understand when the loop continues
						self.logger.debug("Continuing to listen for messages...")

			finally:
				self.curr_connections -= 1
				self.logger.info(f"Battle finished. Current connections: {self.curr_connections}")

	async def periodically_send_disclosure(self, ps_websocket_client, interval=120):
		"""
		This function will periodically call the `disclosureAboutHowToTurnOff` method every `interval` seconds.
		"""
		while True:
			try:
				await self.disclosureAboutHowToTurnOff(ps_websocket_client)
			except Exception as e:
				self.logger.error(f"Error in sending disclosure: {e}")

		# Sleep for the specified interval (in seconds)
		await asyncio.sleep(interval)

	async def disclosureAboutHowToTurnOff(self, ps_websocket_client: PSWebsocketClient):
		"""
		This method sends an informational message to the room about how to turn off the bot.
		"""
		await ps_websocket_client.send_message("", ["""Hello, my name is {}. I'll provide commentary on your pokemon battle.
											  If you want me to stop at anytime, please type \"{}\" and I will leave.""".format(BOT_NAME, BOT_STOP_PHRASE)])

	def stop_command_present(self, message: str) -> bool:
		"""
		This method scans each line of incoming messages from the Pokémon Showdown room for a user chat message 
		that includes the stop phrase (BOT_STOP_PHRASE). If the stop phrase is detected, return True.
		"""
		# Split the message into lines and make the stop phrase case-insensitive
		msg_lines = message.split('\n')
		stop_phrase = BOT_STOP_PHRASE.lower()

		# Check each line for the stop phrase
		for line in msg_lines:
			# Ensure the line starts with "|c|" indicating it's a user chat message
			if line.startswith("|c|"):

				# Check if the user message contains the stop phrase
				if stop_phrase in line.lower():
					self.logger.info(f"Stop command detected.")
					return True

		# If no stop phrase is found, return False
		return False

