#PrimePackage v1.1.4

#to install pip install primepackage 

#import primepackage

#This package defines primes as solutions to the riemann hypothesis. therefore all prime products are also treated as primes i.e 3*5 = 15 15v is a prime product and therefore treated as prime

#FUNCTIONS
randomprime()
primelist()
riemannlist()
isprime()
isriemann()

#to calculate a random prime = primepackage.randomprime(seed) seed can be left empty but will return a value less than 589.  
#if a seed is passed into randomprime() it is possible to calculate larger prime values. 

#primelist() returns a list of prime numbers package.primelist(start, end) returns a list of primes from the start and up to the end 

#riemannlist() works as primelist does

#isprime() and isriemann() return a boolean value for if the number is a prime/prime product or Riemann non trivial zero (rounded to the nearest integer)

#NEW FUNCTIONS


firstquadprime(start,end, n)

returns a list of first quadrant primes between the start and end values that are on the plane n

fourthquadprime(start, end, n)

returns a list of fourth quadrant primes between the start and end values that are on the plane n

superprime(start, end, n)

returns a list of super primes between the start and end values that are on the plane n

subprime(start, end, n)

returns a list of sub primes between the start and end values that are on the plane n

superfirstprime(start, end, n)

returns a list of super first quadrant primes between the start and end values that are on the plane n

superfourthprime(start, end, n)

returns a list of super fourth quadrant primes between the start and end values that are on the plane n

subfirstprime(start, end, n)

returns a list of sub first quadrant primes between the start and end values that are on the plane n

subfourthprime(start, end, n)

returns a list of sub fourth primes between the start and end values that are on the plane n

aprime(index, quadrant, position,plane)

returns a single prime of a specified index, on a specfied quadrant 1 or 4, in a given position super, or sub on plane from 2 onwards. 





