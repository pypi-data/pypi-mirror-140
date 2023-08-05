# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fast_job', 'fast_job.sonyflake']

package_data = \
{'': ['*']}

install_requires = \
['APScheduler>=3.8.1,<4.0.0', 'fastapi>=0.74.1,<0.75.0', 'redis>=4.1.4,<5.0.0']

setup_kwargs = {
    'name': 'fast-job',
    'version': '0.1.9',
    'description': 'a distributed scheduled task scheduling component written for fast-api',
    'long_description': '### fast_job \n- name = "fast_job"\n- description = "Provides scheduling apis and scheduling and task-related services"\n- authors = ["Euraxluo <euraxluo@qq.com>"]\n- license = "The MIT LICENSE"\n- repository = "https://github.com/Euraxluo/fast_job"\n- coverage : 74%\n- version : 0.1.*\n\n![test-report](https://gitee.com/Euraxluo/images/raw/master/pycharm/MIK-HQpicL.png)\n\n#### install\n`pip install fast-job`\n\n#### UseAge\n\n1.wrapper function to build task\n\n```\nfrom fast_job import *\n\n\n@schedule.task(\'task1\', summer="test_task_1", tag=\'test\', description="test_task_1")\ndef test(tag: int):\n    print({"msg": "test_task_1", "tag": tag})\n    return {"msg": "test_task_1", "tag": tag}\n\n\n@schedule.task(\'task2\', summer="test_task_2", tag=\'test\', description="test_task_2")\ndef test2(tag: int):\n    print({"msg": "test_task_2", "tag": tag})\n    return {"msg": "test_task_2", "tag": tag}\n\n\n@schedule.task(\'task3\', summer="test_task_3", tag=\'test\', description="test_task_3")\ndef task3(tag: int):\n    raise Exception(str({"msg": "test_task_2", "tag": tag}))\n```\n\n2.include in your fastApi\n\n```python\nfrom loguru import logger\nfrom fastapi import FastAPI\nfrom example.jobs import schedule, fast_job_api_router\nfrom example.conftest import rdb as redis\n\napp = FastAPI()\n\n\n@app.on_event("startup")\nasync def registry_schedule():\n    schedule.setup(prefix=\'test:\', logger=logger, redis=redis, distributed=True)\n\n\n@app.on_event("shutdown")  # 关闭调度器\nasync def shutdown_connect():\n    schedule.shutdown()\n\n\nprefix = "/test"\napp.include_router(fast_job_api_router, prefix=prefix, tags=["jobs"])  # include router\n```',
    'author': 'Euraxluo',
    'author_email': 'euraxluo@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Euraxluo/fast_job',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
