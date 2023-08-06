# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rx',
 'rx.core',
 'rx.core.abc',
 'rx.core.observable',
 'rx.core.observer',
 'rx.core.operators',
 'rx.core.operators.connectable',
 'rx.disposable',
 'rx.internal',
 'rx.operators',
 'rx.scheduler',
 'rx.scheduler.eventloop',
 'rx.scheduler.mainloop',
 'rx.subject',
 'rx.testing']

package_data = \
{'': ['*']}

modules = \
['py']
setup_kwargs = {
    'name': 'reactivex',
    'version': '4.0.0a3',
    'description': 'Reactive Extensions (Rx) for Python',
    'long_description': '==========================================\nThe Reactive Extensions for Python (RxPY)\n==========================================\n\n.. image:: https://github.com/ReactiveX/RxPY/workflows/Python%20package/badge.svg\n    :target: https://github.com/ReactiveX/RxPY/actions\n    :alt: Build Status\n\n.. image:: https://img.shields.io/coveralls/ReactiveX/RxPY.svg\n    :target: https://coveralls.io/github/ReactiveX/RxPY\n    :alt: Coverage Status\n\n.. image:: https://img.shields.io/pypi/v/rx.svg\n    :target: https://pypi.python.org/pypi/Rx\n    :alt: PyPY Package Version\n\n.. image:: https://img.shields.io/readthedocs/rxpy.svg\n    :target: https://readthedocs.org/projects/rxpy/builds/\n    :alt: Documentation Status\n\n\n*A library for composing asynchronous and event-based programs using observable collections and\nquery operator functions in Python*\n\nReactiveX for Python (RxPY) v4.0\n--------------------------------\n\nFor v3.X please go to the `v3 branch <https://github.com/ReactiveX/RxPY/tree/master>`_.\n\nRxPY v4.x runs on `Python <http://www.python.org/>`_ 3.7 or above. To install\nRxPY:\n\n.. code:: console\n\n    pip3 install reactivex\n\n\nAbout ReactiveX\n------------------\n\nReactive Extensions for Python (RxPY) is a set of libraries for composing\nasynchronous and event-based programs using observable sequences and pipable\nquery operators in Python. Using Rx, developers represent asynchronous data\nstreams with Observables, query asynchronous data streams using operators, and\nparameterize concurrency in data/event streams using Schedulers.\n\n.. code:: python\n\n    import rx\n    from rx import operators as ops\n\n    source = rx.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon")\n\n    composed = source.pipe(\n        ops.map(lambda s: len(s)),\n        ops.filter(lambda i: i >= 5)\n    )\n    composed.subscribe(lambda value: print("Received {0}".format(value)))\n\n\nLearning RxPY\n--------------\n\nRead the `documentation\n<https://rxpy.readthedocs.io/en/latest/>`_ to learn\nthe principles of RxPY and get the complete reference of the available\noperators.\n\nIf you need to migrate code from RxPY v1.x, read the `migration\n<https://rxpy.readthedocs.io/en/latest/migration.html>`_ section.\n\nThere is also a list of third party documentation available `here\n<https://rxpy.readthedocs.io/en/latest/additional_reading.html>`_.\n\n\nCommunity\n----------\n\nJoin the conversation on Slack!\n\nThe gracious folks at `PySlackers <https://pyslackers.com/>`_ have given us a home\nin the `#rxpy <https://pythondev.slack.com/messages/rxpy>`_ Slack channel. Please\njoin us there for questions, conversations, and all things related to RxPy.\n\nTo join, navigate the page above to receive an email invite. After signing up,\njoin us in the #rxpy channel.\n\nPlease follow the community guidelines and terms of service.\n\n\nDifferences from .NET and RxJS\n------------------------------\n\nRxPY is a fairly complete implementation of\n`Rx <http://reactivex.io/>`_ with more than\n`120 operators <https://rxpy.readthedocs.io/en/latest/operators.html>`_, and\nover `1300 passing unit-tests <https://coveralls.io/github/ReactiveX/RxPY>`_. RxPY\nis mostly a direct port of RxJS, but also borrows a bit from RxNET and RxJava in\nterms of threading and blocking operators.\n\nRxPY follows `PEP 8 <http://legacy.python.org/dev/peps/pep-0008/>`_, so all\nfunction and method names are lowercase with words separated by underscores as\nnecessary to improve readability.\n\nThus .NET code such as:\n\n.. code:: c#\n\n    var group = source.GroupBy(i => i % 3);\n\n\nneed to be written with an ``_`` in Python:\n\n.. code:: python\n\n    group = source.pipe(ops.group_by(lambda i: i % 3))\n\nWith RxPY you should use `named keyword arguments\n<https://docs.python.org/3/glossary.html>`_ instead of positional arguments when\nan operator has multiple optional arguments. RxPY will not try to detect which\narguments you are giving to the operator (or not).\n',
    'author': 'Dag Brattli',
    'author_email': 'dag@brattli.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://reactivex.io',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
