# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymarko']

package_data = \
{'': ['*']}

install_requires = \
['colorama']

setup_kwargs = {
    'name': 'pymarko',
    'version': '0.3.1',
    'description': 'A multicast framework and tools',
    'long_description': '# PyMarko\n\n**in development**\n\n## Example\n\n``` python\n#!/usr/bin/env python3\n\nimport time\nfrom pymarko import get_ip\nimport sys\nfrom pymarko.pubsub import Subscriber, Publisher\n\n\ndef subfunc():\n\n    def myfunc(data):\n        if data:\n            msg = data.decode(\'utf8\')\n            print(f">> Subscriber got: {msg}")\n\n    sub = Subscriber()\n    # sub.bind("bob", 9500)\n    sub.connect("bob", get_ip(), 9500)\n    sub.subscribe(myfunc)\n    sub.loop()\n\ndef pubfunc():\n    pub = Publisher()\n    pub.bind("bob", 9500)\n    pub.listen()\n\n    i = 0\n    while True:\n        msg = f"hello {i}".encode("utf8")\n        pub.publish(msg)\n        time.sleep(1)\n        i += 1\n\n\nif __name__ == "__main__":\n\n    if len(sys.argv) > 1:\n        func = sys.argv[1]\n    else:\n        func = "p"\n\n    try:\n        if func == "s":\n            subfunc()\n        elif func == "p":\n            pubfunc()\n\n    except KeyboardInterrupt:\n        print("shutting down")\n    finally:\n        print("end ------------------")\n```\n\n# MIT License\n\n**Copyright (c) 2018 Kevin J. Walchko**\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n',
    'author': 'walchko',
    'author_email': 'walchko@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/pymarko/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
