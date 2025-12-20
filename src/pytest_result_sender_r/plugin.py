from datetime import datetime

import pytest
import requests

data = {"passed": 0, "failed": 0}


def pytest_runtest_logreport(report: pytest.TestReport):
    if report.when == "call":
        print("本次用例执行的结果", report.outcome)
        data[report.outcome] += 1


def pytest_collection_finish(session: pytest.Session):
    data["total"] = len(session.items)
    print(session.items)


def pytest_configure():
    # pytest配置文件加载完毕之后 即测试用例执行之前执行
    data["start_time"] = datetime.now()
    # print(f"{datetime.now()}  pytest开始执行")


def pytest_unconfigure():
    # pytest配置卸载完毕之后 即测试用例执行之后执行
    data["end_time"] = datetime.now()
    # print(f"{datetime.now()}  pytest结束执行")

    data["duration"] = data["end_time"] - data["start_time"]
    data["pass_ratio"] = data["passed"] / data["total"] * 100
    data["pass_ratio"] = f"{data['pass_ratio']:.2f}%"
    # print(data)
    # assert timedelta(seconds=3) >= data['duration'] >= timedelta(seconds=2.5)
    # assert data['total'] == 3
    # assert data['passed'] == 1
    # assert data['failed'] == 2
    # # print(data['pass_ratio'])
    # assert data['pass_ratio'] == '33.33%'

    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=5e54217d-f6c6-4c02-885e-0e8c253c23e4"

    content = f"""pytest自动化测试结果

    测试时间：{data['end_time']} 
    用例数量：{data['total']}
    执行时长：{data['duration']}s 
    测试通过：<font color='green'>{data['passed']}</font>
    测试失败：<font color='red'>{data['failed']}</font>
    测试通过率：{data['pass_ratio']}% 
    测试报告地址：http://baidu.com
    """

    requests.post(url, json={"msgtype": "markdown", "markdown": {"content": content}})
