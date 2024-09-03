import unittest
from showdown.battle_bots.llm.llm_helpers import parse_llm_output, generate_prompt_with_context
from showdown.battle_bots.safest.main import BattleBot as SafestBattleBot

from unittest.mock import patch, MagicMock

class TestParseLLMOutput(unittest.TestCase):
    def test_parse_output_valid_move(self):
        llm_out = """CHOICE:
            move Dragon Ascent
            END"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["Dragon Ascent"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_valid_move_with_other_noise(self):
        llm_out = """LLM puts some preamble about its CHOICE:
            move Dragon Ascent
            END
            Make sure we can tune out some other gibberish here."""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["Dragon Ascent"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_valid_move_and_tera(self):
        llm_out = """CHOICE:
            move Dragon Ascent
            terastallize Flying
            END"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["Dragon Ascent", "terastallize Flying"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_multiple_times_picks_first_match(self):
        llm_out = """CHOICE:
            move Dragon Ascent
            move Tackle
            END"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["Dragon Ascent"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_move_and_switch_only_takes_move(self):
        llm_out = """CHOICE:
            move Dragon Ascent
            END
            CHOICE:
            switch Pikachu
            END"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["Dragon Ascent"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_no_specified_move_should_fail(self):
        llm_out = """CHOICE:
            move
            END"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = None
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_empty_string_should_fail(self):
        llm_out = ""
        parsed_out = parse_llm_output(llm_out)
        expected_out = None
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_valid_switch(self):
        llm_out = """CHOICE:
            switch Kyogre
            END"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["switch Kyogre"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_excess_whitespace_succeeds(self):
        llm_out = """CHOICE: \n\nswitch Kyogre\nEND    """
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["switch Kyogre"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_no_whitespace_succeeds(self):
        llm_out = """CHOICE:switch Kyogre END"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["switch Kyogre"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_switch_with_no_specified_target_should_fail(self):
        llm_out = """CHOICE:
            switch
            END"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = None
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_tera_with_switch_should_not_register(self):
        llm_out = """CHOICE:
            switch Kyogre
            END
            terastallize Flying
            END"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = ["switch Kyogre"]
        self.assertEqual(expected_out, parsed_out)

    def test_parse_output_invalid_response_format_should_fail(self):
        llm_out = """not following the expected format at all"""
        parsed_out = parse_llm_output(llm_out)
        expected_out = None
        self.assertEqual(expected_out, parsed_out)

class TestLLMPromptFormatting(unittest.TestLoader):
	# Test for a typical scenario
	def test_format_prompt_typical_case():
		parsed_state = {
			"user": {"active": "Pikachu", "reserve": ["Charmander", "Bulbasaur"]},
			"opponent": {"active": "Squirtle", "reserve": ["Rattata"]},
		}
		user_options = ['volt tackle', 'switch Charmander', 'switch Bulbasaur']
		opponent_options = ['tackle']
		move_damages = {'volt tackle': 100}

		# Mocking ChatPromptTemplate and related methods
		with patch("showdown.battle_bots.llm.llm_helpers.ChatPromptTemplate") as MockChatPromptTemplate:
			mock_chat_template = MagicMock()
			MockChatPromptTemplate.from_messages.return_value = mock_chat_template
			mock_chat_template.format.return_value = "formatted prompt"

			# Call the function
			result = format_prompt(user_options, opponent_options, move_damages, parsed_state, 1)

			# Check that the method returns the expected result
			assert result == "formatted prompt"

			# Ensure the ChatPromptTemplate was created with the correct messages
			MockChatPromptTemplate.from_messages.assert_called_once()

			# Ensure the format method was called with the correct arguments
			mock_chat_template.format.assert_called_once_with(
				user_options=user_options,
				moves_and_damages=move_damages,
				user_reserve=["Charmander", "Bulbasaur"],
				opponent_pokemon="Squirtle",
				opponent_options=opponent_options,
				num_opp_reserve=1,
				opponent_known_reserve=["Rattata"]
			)

	def test_format_prompt_missing_user_active():
		parsed_state = {
			"user": {"reserve": ["Charmander", "Bulbasaur"]},
			"opponent": {"active": "Squirtle", "reserve": ["Rattata"]},
		}
		user_options = ['volt tackle', 'switch Charmander', 'switch Bulbasaur']
		opponent_options = ['tackle']
		move_damages = {'volt tackle': 100}

		result = format_prompt(user_options, opponent_options, move_damages, parsed_state, 1)

		# Expect the function to return None since 'active' is missing
		assert result is None

	def test_format_prompt_missing_user_options_empty():
		parsed_state = {
			"user": {"active": "Pikachu", "reserve": ["Charmander", "Bulbasaur"]},
			"opponent": {"active": "Squirtle", "reserve": ["Rattata"]},
		}
		user_options = []
		opponent_options = ['tackle']
		move_damages = {'volt tackle': 100}

		result = format_prompt(user_options, opponent_options, move_damages, parsed_state)

		# Expect the function to return None since 'active' is missing
		assert result is None

	def test_format_prompt_empty_opponent_reserve():
		parsed_state = {
			"user": {"active": "Pikachu", "reserve": ["Charmander", "Bulbasaur"]},
			"opponent": {"active": "Squirtle", "reserve": []},
		}
		user_options = ['volt tackle', 'switch Charmander', 'switch Bulbasaur']
		opponent_options = ['tackle']
		move_damages = {'volt tackle': 100}

		with patch("showdown.battle_bots.llm.llm_helpers.ChatPromptTemplate") as MockChatPromptTemplate:
			mock_chat_template = MagicMock()
			MockChatPromptTemplate.from_messages.return_value = mock_chat_template
			mock_chat_template.format.return_value = "formatted prompt"

			result = format_prompt(user_options, opponent_options, move_damages, parsed_state, 0)

			assert result == "formatted prompt"
			mock_chat_template.format.assert_called_once_with(
				user_options=user_options,
				moves_and_damages=move_damages,
				user_reserve=["Charmander", "Bulbasaur"],
				opponent_pokemon="Squirtle",
				opponent_options=opponent_options,
				num_opp_reserve=0,
				opponent_known_reserve=[]
			)
