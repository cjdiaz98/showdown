import unittest
from unittest.mock import AsyncMock
from showdown.Commentary.spectator import Spectator 
from showdown.Commentary.constants import * 

class TestSpectator(unittest.TestCase):
    def setUp(self):
        # Set up the test with a mock PSWebsocketClient and room_name
        self.ps_websocket_client = AsyncMock()
        self.room_name = "test_room"
        self.bot = Spectator()  # Assuming your class is Spectator
        self.bot.logger = AsyncMock()  # Mock the logger to avoid actual logging during tests
        
    def test_stop_command_found_single_line(self):
        # Test case where the stop command is found in a single-line message
        message = "|c|user|Please {} right now.".format(BOT_STOP_PHRASE)
        result =  self.bot.stop_command_present(message)
        self.assertTrue(result)

    def test_stop_command_found_multiple_lines(self):
        # Test case where the stop command is found in a multi-line message
        message = "|c|user|First line.\n|c|user|{} in the second line.".format(BOT_STOP_PHRASE)
        result =  self.bot.stop_command_present(message)
        self.assertTrue(result)

    def test_stop_command_not_found(self):
        # Test case where the stop command is not found in the message
        message = "|c|user|This message does not contain the stop phrase."
        result =  self.bot.stop_command_present(message)
        self.assertFalse(result)

    def test_stop_command_case_insensitive(self):
        # Test case where the stop command is in different case
        message = "|c|user|Please {} right now.".format(BOT_STOP_PHRASE.upper())
        result =  self.bot.stop_command_present(message)
        self.assertTrue(result)

    def test_stop_command_not_chat_message(self):
        # Test case where the message is not a user chat message (no "|c|" prefix)
        message = "|something|random|This is not a chat message."
        result =  self.bot.stop_command_present(message)
        self.assertFalse(result)

    def test_empty_message(self):
        # Test case where the message is empty
        message = ""
        result =  self.bot.stop_command_present(message)
        self.assertFalse(result)