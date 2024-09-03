import unittest
from showdown.battle_bots.llm.llm_helpers import parse_llm_output, generate_prompt_with_context
from showdown.battle import Battle
from unittest.mock import patch, MagicMock, create_autospec
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
    def test_generate_prompt_with_context_typical_case(self):
        # Create a mock Battle object
        # to do: probably make this test more meaningful
        mock_battle = create_autospec(Battle, instance=True)
        mock_battle.create_state.return_value = MagicMock()
        mock_battle.get_all_options.return_value = (
            ['volt tackle', 'switch Charmander', 'switch Bulbasaur'],
            ['tackle']
        )

        # Mocking the get_move_damages function
        with patch("showdown.battle_bots.llm.llm_helpers.get_move_damages", return_value={'volt tackle': 100}):
            # Call the function
            result = generate_prompt_with_context(mock_battle)

            # Check that the method returns a non-empty string
            self.assertIsInstance(result, str)
            self.assertTrue(len(result) > 0)

    def test_generate_prompt_with_context_no_user_options(self):
        # Create a mock Battle object
        mock_battle = create_autospec(Battle, instance=True)
        mock_battle.create_state.return_value = MagicMock()
        mock_battle.get_all_options.return_value = (
            [],  # No user options
            ['tackle']
        )

        result = generate_prompt_with_context(mock_battle)

        # Expect the function to return None since there are no user options
        self.assertIsNone(result)

    def test_generate_prompt_with_context_missing_user_active(self):
        # Create a mock Battle object
        mock_battle = create_autospec(Battle, instance=True)
        mock_battle.create_state.return_value = MagicMock()
        mock_battle.get_all_options.return_value = (
            ['volt tackle', 'switch Charmander', 'switch Bulbasaur'],
            ['tackle']
        )

        # Mocking the parse_state function to return a state without 'active' user
        with patch("showdown.battle_bots.llm.llm_helpers.parse_state", return_value={"user": {"reserve": ["Charmander", "Bulbasaur"]}}):
            result = generate_prompt_with_context(mock_battle)

            # Expect the function to return None since 'active' is missing
            self.assertIsNone(result)
