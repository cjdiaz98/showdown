import constants
import asyncio
import logging
from showdown.websocket_client import PSWebsocketClient
from showdown.Commentary.LLMCommentator import LLMCommentator
from showdown.Commentary.parsingUtils import chunk_message_smartly

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

				# Read logs from the battle
				await self.read_logs_from_battle(ps_websocket_client, room_name)
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
				# f.close()
				self.curr_connections -= 1
				self.logger.info(f"Battle finished. Current connections: {self.curr_connections}")
