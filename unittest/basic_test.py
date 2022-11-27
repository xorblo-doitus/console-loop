import unittest
from unittest.mock import patch


from sys import path
path.clear()
path.append(".")

import console_loop as CL


class InfiniteLoopError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("The loop was not stopped by commands, stopping due to inifite loop prevention.", *args)


def no_stop_error() -> None:
    """A function thaht force closing console_loop to prevent from being stuck in the infinite loop while testing."""
    if CL.enabled:
        CL.enabled = False
        raise InfiniteLoopError()

default_post_funcs = CL.post_funcs.copy()
default_post_funcs.append(no_stop_error)


class TestCommands(unittest.TestCase):
    def setUp(self) -> None:
        """Reseting everythin."""

        CL._cmd_variables.clear()
        CL.post_funcs = default_post_funcs.copy()


    @patch("console_loop.input", return_value="void _")
    def test_force_stop(self, _) -> None:
        """Verifying the loop can be force stopped."""

        with self.assertRaises(InfiniteLoopError, msg="The post_funcs doesn't forcely stop the loop to prevent infinite loop !"):
            CL.enabled = True
            for function in CL.post_funcs: function()

        if CL.enabled:
            self.assertTrue(CL.enabled, "The loop was not stopped from the forcing stop function. Inifinite loop possible.")
            return

        with self.assertRaises(InfiniteLoopError, msg="The loop can't be stopped, even if the post function that prevent it is here !"):
            CL.start_loop()


    @patch("console_loop.input", return_value="stop")
    def test_stop(self, _) -> None:
        """Verifying the stop function"""

        CL.start_loop()
        self.assertEqual(CL.enabled, False, "`stop` do not stop")


    @patch("console_loop.input", return_value="")
    def test_stop_on_empty_input(self, _) -> None:
        """Verifying stop on empty"""

        tmp = CL.stop_on_empty_input
        CL.stop_on_empty_input = True

        CL.start_loop()
        self.assertEqual(CL.enabled, False, "empty input does not stop with `stop_on_empty_input = True`")

        CL.stop_on_empty_input = tmp


    @patch("console_loop.input", return_value="set variable int 958 set other_var int $variable this_varaible = int $variable stop")
    def test_variable_basics(self, _) -> None:
        """Verifying the basics of variables"""

        CL.start_loop()
        self.assertNotEqual(CL._cmd_variables.get("variable", None), None, "`set` do not create variable.")
        self.assertEqual(CL._cmd_variables.get("variable"), 958, "`int` do not convert.")
        self.assertEqual(CL._cmd_variables.get("other_var"), 958, "`$` do not get variable.")
        self.assertEqual(CL._cmd_variables.get("this_varaible"), 958, "`=` do not create variable.")


    @patch("console_loop.input", return_value="var1 = str 958 function = str set $function test int 958 stop")
    def test_variable_basics(self, _) -> None:
        """Verifying the stop function"""

        CL.start_loop()
        self.assertEqual(CL._cmd_variables.get("var1"), "958", "`string` do not convert to str.")
        self.assertEqual(CL._cmd_variables.get("test"), 958, "`set` do not store functions.")


if __name__ == '__main__':
    unittest.main()