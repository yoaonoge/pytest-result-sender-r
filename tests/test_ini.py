import textwrap
from pathlib import Path

import pytest

from pytest_result_sender_r import plugin

pytest_plugins = ["pytester"]


@pytest.fixture(autouse=True)
def mock():
    back_data = plugin.data
    plugin.data = {"passed": 0, "failed": 0}
    # 创建一个干净的测试环境
    yield
    # 恢复测试环境
    plugin.data = back_data


@pytest.mark.parametrize("send_when", ["every", "on_fail"])
def test_send_when(send_when, pytester: pytest.Pytester, tmp_path: Path):
    config_path = tmp_path.joinpath("pytest.ini")  # 生成配置文件
    config_path.write_text(
        textwrap.dedent(
            f"""
        [pytest]
        send_when = {send_when}
        send_api = https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=5e54217d-f6c6-4c02-885e-0e8c253c23e4
        """
        ).lstrip()
    )
    # 断言 配置加载成功
    config = pytester.parseconfig(config_path)  # 把加载出来的配置结果保存在config变量中
    assert config.getini("send_when") == send_when
    #
    pytester.makepyfile(  # 构造场景，用例全部测试通过
        """
        def test_pass():
        ..."""
    )
    pytester.runpytest("-c", str(config_path))
    # 如何断言，插件到底有没有发送结果？
    # 配置文件是否ok  要的话就是1 否则就是不发送
    print(plugin.data)
    if send_when == "every":
        assert plugin.data["send_done"] == 1
    else:
        assert plugin.data.get("send_done") is None


@pytest.mark.parametrize(
    "send_api",
    [
        "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=5e54217d-f6c6-4c02-885e-0e8c253c23e4",
        "",
    ],
)
def test_send_api(send_api, pytester: pytest.Pytester, tmp_path: Path):
    config_path = tmp_path.joinpath("pytest.ini")  # 生成配置文件
    config_path.write_text(
        textwrap.dedent(
            f"""
            [pytest]
            send_when = every
            send_api = {send_api}
            """
        ).lstrip()
    )
    # 断言 配置加载成功
    config = pytester.parseconfig(config_path)  # 把加载出来的配置结果保存在config变量中
    assert config.getini("send_api") == send_api
    #
    pytester.makepyfile(  # 构造场景，用例全部测试通过
        """
        def test_pass():
        ..."""
    )
    pytester.runpytest("-c", str(config_path))
    # 如何断言，插件到底有没有发送结果？
    # 配置文件是否ok  要的话就是1 否则就是不发送
    if send_api:
        assert plugin.data["send_done"] == 1
    else:
        assert plugin.data.get("send_done") is None
