import pytest

from asyncio_tcp_messages_team_2.main import correct_command_and_args


@pytest.mark.asyncio
async def test_standart_input_data_correct_args():
    command, args = await correct_command_and_args("set_data --key key val --val 21 12")
    assert (command, args) == ("set_data", dict(key="21", val="12"))


@pytest.mark.asyncio
async def test_no_keys_correct_args():
    command, args = await correct_command_and_args("set_data --key --val 21 12")
    assert (command, args) == ("Error: ", "No keys or values were passed")


@pytest.mark.asyncio
async def test_no_vals_correct_args():
    command, args = await correct_command_and_args("set_data --key key val --val")
    assert (command, args) == ("Error: ", "No keys or values were passed")


@pytest.mark.asyncio
async def test_no_one_vals_correct_args():
    command, args = await correct_command_and_args("set_data --key key val --val 21")
    assert (command, args) == (
        "Error: ", f"The number of keys differs from the arguments keys: {2}, vals: {1}")
