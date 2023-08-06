# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['charmonium', 'charmonium.cache']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.3.0,<21.0.0',
 'bitmath>=1.3.3,<2.0.0',
 'charmonium.determ-hash>=0.2.0,<0.3.0',
 'charmonium.freeze>=0.5.1,<0.6.0',
 'fasteners>=0.16,<0.17']

entry_points = \
{'console_scripts': ['cache = charmonium.cache._cli:main']}

setup_kwargs = {
    'name': 'charmonium.cache',
    'version': '1.2.5',
    'description': 'Provides a decorator for caching a function and an equivalent command-line util.',
    'long_description': '================\ncharmonium.cache\n================\n\n.. image: https://img.shields.io/pypi/dm/charmonium.cache\n   :alt: PyPI Downloads\n.. image: https://img.shields.io/pypi/l/charmonium.cache\n   :alt: PyPI Downloads\n.. image: https://img.shields.io/pypi/pyversions/charmonium.cache\n   :alt: Python versions\n.. image: https://img.shields.io/github/stars/charmoniumQ/charmonium.cache?style=social\n   :alt: GitHub stars\n.. image: https://img.shields.io/librariesio/sourcerank/pypi/charmonium.cache\n   :alt: libraries.io sourcerank\n\n- `PyPI`_\n- `GitHub`_\n- `Docs`_\n\nProvides a decorator for caching a function. Whenever the function is called\nwith the same arguments, the result is loaded from the cache instead of\ncomputed. This cache is **persistent across runs**. If the arguments, source\ncode, or enclosing environment have changed, the cache recomputes the data\ntransparently (**no need for manual invalidation**).\n\nThe use case is meant for iterative development, especially on scientific\nexperiments. Many times a developer will tweak some of the code but not\nall. Often, reusing intermediate results saves a significant amount of time\nevery run.\n\nQuickstart\n----------\n\nIf you don\'t have ``pip`` installed, see the `pip install\nguide`_. Then run:\n\n::\n\n    $ pip install charmonium.cache\n\n.. code:: python\n\n    >>> from charmonium.cache import memoize\n    >>> i = 0\n    >>> @memoize()\n    ... def square(x):\n    ...     print("recomputing")\n    ...     # Imagine a more expensive computation here.\n    ...     return x**2 + i\n    ...\n    >>> square(4)\n    recomputing\n    16\n    >>> square(4) # no need to recompute\n    16\n    >>> i = 1\n    >>> square(4) # global i changed; must recompute\n    recomputing\n    17\n\nAdvantages\n----------\n\nWhile there are other libraries and techniques for memoization, I believe this\none is unique because it is:\n\n1. **Correct with respect to source-code changes:** The cache detects if you\n   edit the source code or change a file which the program reads (provided they\n   use this library\'s right file abstraction). Users never need to manually\n   invalidate the cache, so long as the functions are pure (unlike\n   `joblib.Memory`_, `Klepto`_).\n\n   It is precise enough that it will ignore changes in unrelated functions in\n   the file, but it will detect changes in relevant functions in other files. It\n   even detects changes in global variables (as in the example above). See\n   `Detecting Changes in Functions`_ for details.\n\n2. **Useful between runs and across machines:** The cache can persist on the\n   disk (unlike `functools.lru_cache`_). Moreover, a cache can be shared on the\n   network, so that if *any* machine has computed the function for the same\n   source-source and arguments, this value can be reused by *any other* machine,\n   provided your datatype is de/serializable on those platforms.\n\n3. **Easy to adopt:** Only requires adding one line (`decorator`_) to\n   the function definition.\n\n4. **Bounded in size:** The cache won\'t take up too much space. This\n   space is partitioned across all memoized functions according to the\n   heuristic.\n\n5. **Supports smart heuristics:** Motivated by academic literature, I use cache\n   policies that can take into account time-to-recompute and storage-size in\n   addition to recency, unlike `LRU`_.\n\n6. **Overhead aware:** The library measures the time saved versus overhead. It\n   warns the user if the overhead of caching is not worth it.\n\nMemoize CLI\n-----------\n\nMake is good for compiling code, but falls short for data science. To get\ncorrect results, you have to incorporate *every* variable your result depends on\ninto a file or part of the filename. If you put it in a file, you only have one\nversion cached at a time; if you put it in the filename, you have to squeeze the\nvariable into a short string. In either case, stale results will accumulate\nunboundedly, until you run ``make clean`` which also purges the fresh\nresults. Finally, it is a significant effor to rewrite shell scripts in make.\n\n``memoize`` makes it easy to memoize steps in shell scripts, correctly. Just add\n``memoize`` to the start of the line. If the command, its arguments,\nor its input files change, then ``command arg1 arg2 ...`` will be\nrerun. Otherwise, the output files (including stderr and stdout) will be\nproduced from a prior run. ``memoize`` uses ptrace to automatically determine\nwhat inputs you depend on and what outputs you produce.\n\n::\n\n   memoize command arg1 arg2\n   # or\n   memoize --key=$(date +%Y-%m-%d) -- command arg1 arg2\n\nSee `CLI`_ for more details.\n\n.. _`LRU`: https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU)\n.. _`decorator`: https://en.wikipedia.org/wiki/Python_syntax_and_semantics#Decorators\n.. _`pip install guide`: https://pip.pypa.io/en/latest/installing/\n.. _`PyPI`: https://pypi.org/project/charmonium.cache/\n.. _`GitHub`: https://github.com/charmoniumQ/charmonium.cache\n.. _`docs`: https://charmoniumq.github.io/charmonium.cache/\n.. _`Detecting Changes in Functions`: https://charmoniumq.github.io/charmonium.cache/tutorial.html#detecting-changes-in-functions\n.. _`Klepto`: https://klepto.readthedocs.io/en/latest/\n.. _`joblib.Memory`: https://joblib.readthedocs.io/en/latest/memory.html\n.. _`functools.lru_cache`: https://docs.python.org/3/library/functools.html#functools.lru_cache\n.. _`CLI`: https://charmoniumq.github.io/charmonium.cache/cli.html\n',
    'author': 'Samuel Grayson',
    'author_email': 'sam+dev@samgrayson.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/charmoniumQ/charmonium.cache.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
