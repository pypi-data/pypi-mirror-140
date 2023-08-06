import pytest

from asyncio_tcp_messages_team_2.main import MySocketLib


@pytest.fixture()
def app_hello():
    app = MySocketLib("1233", 8000)

    @app.command
    async def hello(x: int):
        return x

    yield app


@pytest.mark.asyncio
async def test_add_in_commands_commands_dict(app_hello):
    assert app_hello.commands_dict["hello"]


@pytest.mark.asyncio
async def test_work_func_in_commands_commands_dict(app_hello):
    assert await app_hello.commands_dict["hello"](1) == 1


@pytest.mark.asyncio
async def test_normal_data_check_args(app_hello):
    assert await app_hello.check_args("hello", dict(x="123"))


@pytest.mark.asyncio
async def test_int_data_check_args(app_hello):
    assert await app_hello.check_args("hello", dict(x="123"))


@pytest.mark.asyncio
async def test_cannot_be_converted_to_int_data_check_args(app_hello):
    assert not await app_hello.check_args("hello", dict(x="1a3"))


@pytest.mark.asyncio
async def test_another_key_data_check_args(app_hello):
    assert not await app_hello.check_args("hello", dict(y="12"))


@pytest.mark.asyncio
async def test_output_data(app_hello):
    result = await app_hello.output_data("hello --key x --val 21")
    assert result == "21\n"


@pytest.mark.asyncio
async def test_no_output_data():
    app = MySocketLib("1233", 8000)

    @app.command
    async def hello(x: int):
        pass

    result = await app.output_data("hello --key x --val 21")
    assert result == "ok\n"


@pytest.mark.asyncio
async def test_wrong_command_output_data(app_hello):
    result = await app_hello.output_data("hell0 --key x --val 21")
    assert result == "Wrong arguments ot command\n"


@pytest.mark.asyncio
async def test_wrong_argument_output_data(app_hello):
    result = await app_hello.output_data("hello --key y --val 21")
    assert result == "Wrong arguments ot command\n"


@pytest.mark.asyncio
async def test_wrong_output_data(app_hello):
    result = await app_hello.output_data("hello --key x --val 21 21")
    assert result == "Error: The number of keys differs from the arguments keys: 1, vals: 2\n"
