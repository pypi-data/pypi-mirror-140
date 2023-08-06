# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['loopmon']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=3.8']

setup_kwargs = {
    'name': 'loopmon',
    'version': '1.0.0',
    'description': 'Lightewight monitor library for asyncio.EventLoop',
    'long_description': "# loopmon - Lightweight Event Loop monitoring\n\n\n[![Codecov](https://img.shields.io/codecov/c/gh/isac322/loopmon?style=flat-square&logo=codecov)](https://app.codecov.io/gh/isac322/loopmon)\n[![Dependabot Status](https://flat.badgen.net/github/dependabot/isac322/loopmon?icon=github)](https://github.com/isac322/loopmon/network/dependencies)\n[![PyPI](https://img.shields.io/pypi/v/loopmon?label=pypi&logo=pypi&style=flat-square)](https://pypi.org/project/loopmon/)\n[![PyPI - Wheel](https://img.shields.io/pypi/wheel/loopmon?style=flat-square&logo=pypi)](https://pypi.org/project/loopmon/)\n[![Python Version](https://img.shields.io/pypi/pyversions/loopmon.svg?style=flat-square&logo=python)](https://pypi.org/project/loopmon/)\n[![GitHub last commit (branch)](https://img.shields.io/github/last-commit/isac322/loopmon/master?logo=github&style=flat-square)](https://github.com/isac322/loopmon/commits/master)\n[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/isac322/loopmon/CI/master?logo=github&style=flat-square)](https://github.com/isac322/loopmon/actions)\n[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)\n\nloopmon is a lightweight library that can detect throttling of event loops.\nFor example, you can detect long-running coroutine or whether the blocking function is invoked inside the event loop.\n\n\n## Usage\n\n```python\nimport asyncio\nimport time\nfrom datetime import datetime\nimport loopmon\n\nasync def print_collected_data(lag: float, tasks: int, data_at: datetime) -> None:\n    print(f'event loop lag: {lag:.3f}, running tasks: {tasks}, at {data_at}')\n\nasync def main() -> None:\n    loopmon.create(interval=0.5, callbacks=[print_collected_data])\n    # Simple I/O bound coroutine does not occur event loop lag\n    await asyncio.sleep(0.2)\n    # Blocking function call\n    time.sleep(1)\n\nif __name__ == '__main__':\n    asyncio.run(main())\n```\n\nwill prints:\n\n```\nevent loop lag: 0.000, running tasks: 2, at 2022-02-24 13:29:05.367330+00:00\nevent loop lag: 1.001, running tasks: 1, at 2022-02-24 13:29:06.468622+00:00\n```\n\nYou can check other [examples](https://github.com/isac322/loopmon/tree/master/examples).\n\nI recommend you to add `loopmon.create(...)` on beginning of async function if you are not familiar with handling loop itself.\nBut you can also control creation, installation or staring of monitor via `EventLoopMonitor.start()` or `EventLoopMonitor.install_to_loop()`.\n\n## Features\n\n- Detects event loop lag\n  - Detects event loop running on other thread. [example](https://github.com/isac322/loopmon/blob/master/examples/06_monitoring_another_thread.py)\n- Collect how many tasks are running in the event loop\n- Customize monitoring start and end points\n- Customize monitoring interval\n- Customize collected metrics through callbacks\n- 100% type annotated\n- Zero dependency (except `typing-extentions`)\n\n\n## How it works\n\nEvent loop is single threaded and based on Cooperative Scheduling.\nSo if there is a task that does not yield to another tasks, any tasks on the loop can not be executed.\nAnd starvation also happens when there are too many tasks that a event loop can not handle.\n\nCurrently `loopmon.SleepEventLoopMonitor` is one and only monitor implementation.\nIt periodically sleeps with remembering time just before sleep, and compares the time after awake.\nThe starvation happen if the difference bigger than its sleeping interval.\n\n\n#### pseudo code of `SleepEventLoopMonitor`\n\n```python\nwhile True:\n    before = loop.time()\n    await asyncio.sleep(interval)\n    lag = loop.time() - before - interval\n    tasks = len(asyncio.all_tasks(loop))\n    data_at = datetime.now(timezone.utc)\n    for c in callbacks:\n        loop.create_task(c(lag, tasks, data_at))\n```\n\n## Integration examples\n\n### Prometheus\n\n\n```python\nfrom datetime import datetime\nfrom functools import partial\nimport loopmon\nfrom prometheus_client import Gauge\n\nasync def collect_lag(gauge: Gauge, lag: float, _: int, __: datetime) -> None:\n    gauge.set(lag)\n\nasync def main(gauge: Gauge) -> None:\n    loopmon.create(interval=0.5, callbacks=[partial(collect_lag, gauge)])\n    ...\n```",
    'author': 'Byeonghoon Yoo',
    'author_email': 'bh322yoo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/isac322/loopmon',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
