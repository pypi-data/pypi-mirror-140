# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['primepackage']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'primepackage',
    'version': '2.0',
    'description': 'A package for the calculation, querying and lsiting of primes. prime products and non trivial zeros',
    'long_description': '#PrimePackage v1.1.4\n\n#to install pip install primepackage \n\n#import primepackage\n\n#This package defines primes as solutions to the riemann hypothesis. therefore all prime products are also treated as primes i.e 3*5 = 15 15v is a prime product and therefore treated as prime\n\n#FUNCTIONS\nrandomprime()\nprimelist()\nriemannlist()\nisprime()\nisriemann()\n\n#to calculate a random prime = primepackage.randomprime(seed) seed can be left empty but will return a value less than 589.  \n#if a seed is passed into randomprime() it is possible to calculate larger prime values. \n\n#primelist() returns a list of prime numbers package.primelist(start, end) returns a list of primes from the start and up to the end \n\n#riemannlist() works as primelist does\n\n#isprime() and isriemann() return a boolean value for if the number is a prime/prime product or Riemann non trivial zero (rounded to the nearest integer)\n\n#NEW FUNCTIONS\n\n\nfirstquadprime(start,end, n)\n\nreturns a list of first quadrant primes between the start and end values that are on the plane n\n\nfourthquadprime(start, end, n)\n\nreturns a list of fourth quadrant primes between the start and end values that are on the plane n\n\nsuperprime(start, end, n)\n\nreturns a list of super primes between the start and end values that are on the plane n\n\nsubprime(start, end, n)\n\nreturns a list of sub primes between the start and end values that are on the plane n\n\nsuperfirstprime(start, end, n)\n\nreturns a list of super first quadrant primes between the start and end values that are on the plane n\n\nsuperfourthprime(start, end, n)\n\nreturns a list of super fourth quadrant primes between the start and end values that are on the plane n\n\nsubfirstprime(start, end, n)\n\nreturns a list of sub first quadrant primes between the start and end values that are on the plane n\n\nsubfourthprime(start, end, n)\n\nreturns a list of sub fourth primes between the start and end values that are on the plane n\n\naprime(index, quadrant, position,plane)\n\nreturns a single prime of a specified index, on a specfied quadrant 1 or 4, in a given position super, or sub on plane from 2 onwards. \n\n\n\n\n\n',
    'author': 'Jamell Samuels',
    'author_email': 'jamellsamuels@googlemail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
