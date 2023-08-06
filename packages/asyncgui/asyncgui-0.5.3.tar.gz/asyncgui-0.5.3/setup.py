# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asyncgui', 'asyncgui.testing']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'asyncgui',
    'version': '0.5.3',
    'description': 'async/await without event-loop',
    'long_description': '# AsyncGui\n\nA thin layer that helps to build an async/await-based api using a callback-based api.\n\n## How to use\n\nDespite its name, `asyncgui` has nothing to do with gui.\nYou can wrap any kind of callback-based api in it.\nThe simplest example of it would be [sched](https://docs.python.org/3/library/sched.html),\nwhose the whole feature is a timer.\nAll you need is just few lines of code:\n\n```python\nimport types\nimport sched\nimport asyncgui\n\ns = sched.scheduler()\n\n# wrapping the timer api takes only three lines\n@types.coroutine\ndef sleep(duration):\n    yield lambda step_coro: s.enter(duration, 10, step_coro)\n\n\nasync def main():\n    print(\'A\')\n    await sleep(1)  # Now you can sleep in an async-manner\n    print(\'B\')\n    await sleep(1)\n    print(\'C\')\n\nasyncgui.start(main())\ns.run()\n```\n\nAnd you already have a structured concurrency api as well:\n\n```python\nasync def print_numbers():\n    for i in range(10):\n        await sleep(.1)\n        print(i)\n\n\nasync def print_letters():\n    for c in "ABCDE":\n        await sleep(.1)\n        print(c)\n\n\nasync def main():\n    from asyncgui.structured_concurrency import or_\n    # Let print_letters() and print_numbers() race.\n    # As soon as one of them finishes, the other one gets cancelled.\n    tasks = await or_(print_letters(), print_numbers())\n    if tasks[0].done:\n        print("print_letters() won")\n    else:\n        print("print_numbers() won")\n    print(\'main end\')\n```\n\n```\nA\n0\nB\n1\nC\n2\nD\n3\nE\nprint_letters() won\nmain end\n```\n\n## Why not asyncio ?\n\nThe above example may not attract you because you can just replace `sched` with [asyncio](https://docs.python.org/3/library/asyncio.html) or [Trio](https://trio.readthedocs.io/en/stable/),\nand can use thier sleep function (`asyncio.sleep` and `trio.sleep`).\nBut in a read-world situation, that might not be an option:\nKivy required [massive changes](https://github.com/kivy/kivy/pull/6368) in order to adapt to `asyncio` and `Trio`,\n[asyncio-tkinter](https://github.com/fluentpython/asyncio-tkinter)\'s codebase is quite big as well.\n\nThe reason they needed lots of work is that they had to merge two event-loops into one.\nOne is from the gui libraries. The other one is from async libraries.\nYou cannot just simply run multiple event-loops simultaneously in one thread...\nmaybe.\n\nOn the other hand, `asyncgui` doesn\'t require a lot of work as shown above **because it doesn\'t have an event-loop**.\n`asyncgui` and a library who has an event-loop can live in the same thread seemlessly because of it.\n\n## So, is asyncgui superior to asyncio ?\n\nNo, it is not.\nFor `asyncgui`, many features that exist in `asyncio` are either impossible or hard to implement because of the lack of event-loop.\nThus those features need to be specific to each event-loop you are using.\nYou\'ve already witnessed one, the `sleep`.\n\n## asyncgui is not usefull then.\n\nThere is at least one situation where `asyncgui` shines.\nWhen you are creating a gui app, you probably want the app to quickly react to the gui events, like pressing a button.\nThis is problematic for `asyncio` because it cannot immediately start/resume a task.\nIt can schedule a task to *eventually* start/resume but not *immediate*,\nwhich causes to [spill gui events](https://github.com/gottadiveintopython/asynckivy/blob/main/examples/misc/why_asyncio_is_not_suitable_for_handling_touch_events.py).\nAs a result, you need to use callback-based api for that, and thus you cannot fully receive the benefits of async/await.\n\nIf you use `asyncgui`, that never happens because:\n\n- `asyncgui.start()` immediately starts a task.\n- `asyncgui.Event.set()` immediately resumes the tasks waiting for it to happen.\n\nIn summary, if your program needs to react to something immediately, `asyncgui` is for you.\nOtherwise, it\'s probably not worth it.\n\n## Installation\n\nIf you use this module, it\'s recommended to pin the minor version, because if it changed, it means some *important* breaking changes occurred.\n\n```text\npoetry add asyncgui@~0.5\npip install "asyncgui>=0.5,<0.6"\n```\n\n## Tested on\n\n- CPython 3.7\n- CPython 3.8\n- CPython 3.9\n- CPython 3.10\n\n## Async-libraries who relies on this\n\n- [asynckivy](https://github.com/gottadiveintopython/asynckivy)\n- [asynctkinter](https://github.com/gottadiveintopython/asynctkinter)\n',
    'author': 'Nattōsai Mitō',
    'author_email': 'flow4re2c@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gottadiveintopython/asyncgui',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
