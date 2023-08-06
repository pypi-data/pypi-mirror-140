# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sparrow']

package_data = \
{'': ['*']}

install_requires = \
['pyspark>=3.2.1,<4.0.0']

setup_kwargs = {
    'name': 'pysparrow',
    'version': '1.0.4',
    'description': 'An arrow interface for PySpark RDDs',
    'long_description': '# Sparrow\n\nSparrow (a combination of _Spark_ and _arrow_) is a Python mini library that enhances Spark with an _arrow API_.\n\nIntent is to make mappers and filters over RDD a bit more elegant and exciting. Author also feels that here developed API does have a more consitent feel.\n\nConsider and example of few operations on an RDD in native PySpark\n```python\n...\nrdd = spark.sparkContext.parallelize(\n        [\n            (1, 2.0, ["a", "b", "c"]),\n            (2, 3.0, ["b", "c", "d"]),\n            (3, 4.0, ["c", "d", "e"]),\n            (4, 5.0, ["d", "e", "f"]),\n            (5, 6.0, ["e", "f", "g"]),\n        ]\n    )\n    \nres = rdd.map(lambda x: x[2]).flatMap(lambda x: x).filter(lambda x: x == \'b\')\n\n```\nand then on RDD extended with Sparrow:\n```python\nrdd = spark.sparkContext.parallelize(\n        [\n            (1, 2.0, ["a", "b", "c"]),\n            (2, 3.0, ["b", "c", "d"]),\n            (3, 4.0, ["c", "d", "e"]),\n            (4, 5.0, ["d", "e", "f"]),\n            (5, 6.0, ["e", "f", "g"]),\n        ]\n    )\n\nres = (\n    SparrowRDD(rdd) \n    >> (lambda x: x[2]) \n    >> Flatten(lambda x: x)\n    >> Filter(lambda x: x == \'b\')\n)\n```\n',
    'author': 'Peter Vyboch',
    'author_email': 'pvyboch1@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/petereon/sparrow',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
