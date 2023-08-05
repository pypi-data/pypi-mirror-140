#__init__.py

__version__="2.0"

#imports

from random import random
import math
from random import randint


def riemannlist(start, end):
    theta = math.pi /3 
    arr = []
    length = end - start
    # Crazy exception case
    if(length == 0):
        rand = random()
        start = math.floor(length * rand)
        end  = start + length
               
     
    for i in range(start, length):
        y = theta * (1 + 6*i)
        y = math.sqrt((y/theta)**2 - 0.25)
        arr.append(y)
        y = theta* 5 *(1 + (6/5)*i)
        y = math.sqrt((y/theta)-0.25)
        arr.append(y)
        
    arr.sort()
    
    begin = 0
    fini = len(arr)-1
    
    for i in range(0, len(arr)-1):
        if arr[i] <= start:
                begin = i
        if arr[i] < end:
                fini = i
        if begin == 0:
            begin = begin +1
    
    
    arr = arr[begin-1:fini+1]
    
    
    return arr



def primelist(start, end):
    theta = math.pi /3 
    arr = []
    length = end - start
    
    if(length == 0):
        rand = random()
        start = math.floor(length * rand)
        end  = start + length
        
     
    for i in range(start, length):
        y = theta * (1 + 6*i)
        y = math.sqrt((y/theta)**2 - 0.25)
        arr.append(y)
        y = theta* 5 *(1 + (6/5)*i)
        y = math.sqrt((y/theta)-0.25)
        arr.append(y)
        
    arr.sort()

    prime = []
    for i in range(0, len(arr)-1):
        arr[i] = math.floor(arr[i])
        if(math.floor(arr[i]) % 2 != 0):
            arr[i] = arr[i] + 1
        prime.append(arr[i]+1)
        prime.append(arr[i]-1)
       
    prime.sort()
    
    primeh = []
    for i in range(0, len(prime)-1):
        if prime[i] not in primeh:
            primeh.append(prime[i])
    begin = 0
    fini = len(primeh)-1
    
    for i in range(0, len(primeh)-1):
        if primeh[i] <= start:
                begin = i
        if primeh[i] <= end:
                fini = i
        
    
    prime = primeh
    prime = prime[begin:fini]
    
    #set prime[0] = start
    #prime[len(prime)-1] = end
    #slice function copy into riemann list 
    return prime
      
      
      
def randomprime(seed = 100):

    theta = math.pi /3 
    arr = []
    
    length = seed
    
    for i in range(0, length):
        y = theta * (1 + 6*i)
        y = math.sqrt((y/theta)**2 - 0.25)
        arr.append(y)
        y = theta* 5 *(1 + (6/5)*i)
        y = math.sqrt((y/theta)-0.25)
        arr.append(y)
        
    arr.sort()

    prime = []
    for i in range(0, len(arr)):
        arr[i] = math.floor(arr[i])
        if(math.floor(arr[i]) % 2 != 0):
            arr[i] = arr[i] + 1
        prime.append(arr[i]+1)
        prime.append(arr[i]-1)
       
    prime.sort()
    
    primeh = []
    for i in range(0, len(prime)):
        if prime[i] not in primeh:
            primeh.append(prime[i])
        
        
    prime = primeh
    
    r = randint(0, len(prime)-1)
    
    result = prime[r]
    
    return result
    



def isprime(num):
    theta = math.pi/3
    r1 = num + 1
    r2 = num - 1
    length = math.ceil(num/2)
    arr = []
                
    for i in range(0, length):
        y = theta * (1 + 6*i)
        y = math.sqrt((y/theta)**2 - 0.25)
        arr.append(y)
        y = theta* 5 *(1 + (6/5)*i)
        y = math.sqrt((y/theta)-0.25)
        arr.append(y)
        
    arr.sort()
    prime = []
    for i in range(0, len(arr)):
        arr[i] = math.floor(arr[i])
        if(math.floor(arr[i]) % 2 != 0):
            arr[i] = arr[i] + 1
        prime.append(arr[i]+1)
        prime.append(arr[i]-1)
       
    prime.sort()
    
    primeh = []
    for i in range(0, len(prime)):
        if prime[i] not in primeh:
            primeh.append(prime[i])
        
    prime = primeh
    
    return num in prime
        
    



def isriemann(num):
    theta = math.pi/3
    length = math.ceil(num/2)
    arr = []
    result = False
    
    for i in range(0, length):
        y = theta * (1 + 6*i)
        y = math.sqrt((y/theta)**2 - 0.25)
        arr.append(y)
        y = theta* 5 *(1 + (6/5)*i)
        y = math.sqrt((y/theta)-0.25)
        arr.append(y)
        
    arr.sort()
    
    for i in range(0, len(arr)):
        if math.floor(arr[i]) % 2 != 0:
            arr[i] = arr[i] + 1
    
    for i in range(0, len(arr)):
        arr[i] = math.floor(arr[i])
        
    
    return num in arr
        
        

def firstquadprime(start, end,n = 2):
    theta = math.pi /3 
    arr = []
    length = end - start
    
    if(length == 0):
        rand = random()
        start = math.floor(length * rand)
        end  = start + length
        
    for i in range(start, end):
        y = theta * (n-1)* (1 + 6*i)
        y = math.sqrt((y/theta)**2 - 0.25)
        arr.append(y)
        
    arr.sort()

    prime = []
    for i in range(0, len(arr)-1):
        arr[i] = math.floor(arr[i])
        if(math.floor(arr[i]) % 2 != 0):
            arr[i] = arr[i] + 1
        prime.append(arr[i]+1)
        prime.append(arr[i]-1)
       
    prime.sort()
    
    primeh = []
    for i in range(0, len(prime)-1):
        if prime[i] not in primeh:
            primeh.append(prime[i])
    begin = 0
    fini = len(primeh)-1
    
    for i in range(0, len(primeh)-1):
        if primeh[i] <= start:
                begin = i
        if primeh[i] <= end:
                fini = i
        
    
    prime = primeh
    firstquadarr = prime[begin:fini]
    
    return firstquadarr


def fourthquadprime(start, end, n =2):
    theta = math.pi /3 
    arr = []
    length = end - start
    
    if(length == 0):
        rand = random()
        start = math.floor(length * rand)
        end  = start + length
        
    for i in range(start, end):
        y = theta* (n-1)* 5 *(1 + (6/5)*i)
        y = math.sqrt((y/theta)-0.25)
        arr.append(y)
        
    arr.sort()

    prime = []
    for i in range(0, len(arr)-1):
        arr[i] = math.floor(arr[i])
        if(math.floor(arr[i]) % 2 != 0):
            arr[i] = arr[i] + 1
        prime.append(arr[i]+1)
        prime.append(arr[i]-1)
       
    prime.sort()
    
    primeh = []
    for i in range(0, len(prime)-1):
        if prime[i] not in primeh:
            primeh.append(prime[i])
    begin = 0
    fini = len(primeh)-1
    
    for i in range(0, len(primeh)-1):
        if primeh[i] <= start:
                begin = i
        if primeh[i] <= end:
                fini = i
        
    
    prime = primeh
    fourthquadarr = prime[begin:fini]
    
    return fourthquadarr

def superprime(start, end, n = 2):
    theta = math.pi /3 
    arr = []
    length = end - start
    
    if(length == 0):
        rand = random()
        start = math.floor(length * rand)
        end  = start + length
        
    for i in range(start, end):
        y = theta * (n-1)*(1 + 6*i)
        y = math.sqrt((y/theta)**2 - 0.25)
        arr.append(y)
        y = theta* 5 *(1 + (6/5)*i)
        y = math.sqrt((y/theta)-0.25)
        arr.append(y)
        
    arr.sort()

    prime = []
    for i in range(0, len(arr)-1):
        arr[i] = math.floor(arr[i])
        if(math.floor(arr[i]) % 2 != 0):
            arr[i] = arr[i] + 1
        prime.append(arr[i]+1)
       
    prime.sort()
    
    primeh = []
    for i in range(0, len(prime)-1):
        if prime[i] not in primeh:
            primeh.append(prime[i])
    begin = 0
    fini = len(primeh)-1
    
    for i in range(0, len(primeh)-1):
        if primeh[i] <= start:
                begin = i
        if primeh[i] <= end:
                fini = i
        
    
    prime = primeh
    superprimearr = prime[begin:fini]
      
    return superprimearr
        
    
def subprime(start, end, n = 2):
    
    theta = math.pi /3 
    arr = []
    length = end - start
    
    if(length == 0):
        rand = random()
        start = math.floor(length * rand)
        end  = start + length
        
    for i in range(start, end):
        y = theta * (n-1)* (1 + 6*i)
        y = math.sqrt((y/theta)**2 - 0.25)
        arr.append(y)
        y = theta* 5 *(1 + (6/5)*i)
        y = math.sqrt((y/theta)-0.25)
        arr.append(y)
        
    arr.sort()

    prime = []
    for i in range(0, len(arr)-1):
        arr[i] = math.floor(arr[i])
        if(math.floor(arr[i]) % 2 != 0):
            arr[i] = arr[i] + 1
        prime.append(arr[i]-1)
       
    prime.sort()
    
    primeh = []
    for i in range(0, len(prime)-1):
        if prime[i] not in primeh:
            primeh.append(prime[i])
    begin = 0
    fini = len(primeh)-1
    
    for i in range(0, len(primeh)-1):
        if primeh[i] <= start:
                begin = i
        if primeh[i] <= end:
                fini = i
        
    
    prime = primeh
    subprimearr = prime[begin:fini]
    
    return subprimearr

def superfirstprime(start, end, n = 2):
    
    theta = math.pi /3 
    arr = []
    length = end - start
    
    if(length == 0):
        rand = random()
        start = math.floor(length * rand)
        end  = start + length
        
    for i in range(start, end):
        y = theta * (n-1)* (1 + 6*i)
        y = math.sqrt((y/theta)**2 - 0.25)
        arr.append(y)
        
    arr.sort()

    prime = []
    for i in range(0, len(arr)-1):
        arr[i] = math.floor(arr[i])
        if(math.floor(arr[i]) % 2 != 0):
            arr[i] = arr[i] + 1
        prime.append(arr[i]+1)
       
    prime.sort()
    
    primeh = []
    for i in range(0, len(prime)-1):
        if prime[i] not in primeh:
            primeh.append(prime[i])
    begin = 0
    fini = len(primeh)-1
    
    for i in range(0, len(primeh)-1):
        if primeh[i] <= start:
                begin = i
        if primeh[i] <= end:
                fini = i
        
    
    prime = primeh
    superfirstarr = prime[begin:fini]
    
    return superfirstarr


def subfirstprime(start, end, n = 2):
    
    theta = math.pi /3 
    arr = []
    length = end - start
    
    if(length == 0):
        rand = random()
        start = math.floor(length * rand)
        end  = start + length
        
    for i in range(start, end):
        y = theta * (n-1)* (1 + 6*i)
        y = math.sqrt((y/theta)**2 - 0.25)
        arr.append(y)
    
        
    arr.sort()

    prime = []
    for i in range(0, len(arr)-1):
        arr[i] = math.floor(arr[i])
        if(math.floor(arr[i]) % 2 != 0):
            arr[i] = arr[i] + 1
        prime.append(arr[i]-1)
       
    prime.sort()
    
    primeh = []
    for i in range(0, len(prime)-1):
        if prime[i] not in primeh:
            primeh.append(prime[i])
    begin = 0
    fini = len(primeh)-1
    
    for i in range(0, len(primeh)-1):
        if primeh[i] <= start:
                begin = i
        if primeh[i] <= end:
                fini = i
        
    
    prime = primeh
    subfirstarr = prime[begin:fini]
    
    return subfirstarr


def superfourthprime(start, end, n = 2):
    
    theta = math.pi /3 
    arr = []
    length = end - start
    
    if(length == 0):
        rand = random()
        start = math.floor(length * rand)
        end  = start + length
        
    for i in range(start, end):
        y = theta* (n-1)* 5 *(1 + (6/5)*i)
        y = math.sqrt((y/theta)-0.25)
        arr.append(y)
    
        
    arr.sort()

    prime = []
    for i in range(0, len(arr)-1):
        arr[i] = math.floor(arr[i])
        if(math.floor(arr[i]) % 2 != 0):
            arr[i] = arr[i] + 1
        prime.append(arr[i]+1)
       
    prime.sort()
    
    primeh = []
    for i in range(0, len(prime)-1):
        if prime[i] not in primeh:
            primeh.append(prime[i])
    begin = 0
    fini = len(primeh)-1
    
    for i in range(0, len(primeh)-1):
        if primeh[i] <= start:
                begin = i
        if primeh[i] <= end:
                fini = i
        
    
    prime = primeh
    superfourtharr = prime[begin:fini]
    
    return superfourtharr


def subfourthprime(start, end, n = 2):
    
    theta = math.pi /3 
    arr = []
    length = end - start
    
    if(length == 0):
        rand = random()
        start = math.floor(length * rand)
        end  = start + length
        
    for i in range(start, end):
        y = theta* 5 * (n-1) *(1 + (6/5)*i)
        y = math.sqrt((y/theta)-0.25)
        arr.append(y)
     
        
    arr.sort()

    prime = []
    for i in range(0, len(arr)-1):
        arr[i] = math.floor(arr[i])
        if(math.floor(arr[i]) % 2 != 0):
            arr[i] = arr[i] + 1
        prime.append(arr[i]-1)
       
    prime.sort()
    
    primeh = []
    for i in range(0, len(prime)-1):
        if prime[i] not in primeh:
            primeh.append(prime[i])
    begin = 0
    fini = len(primeh)-1
    
    for i in range(0, len(primeh)-1):
        if primeh[i] <= start:
                begin = i
        if primeh[i] <= end:
                fini = i
        
    
    prime = primeh
    subfourtharr = prime[begin:fini]
    
    return subfourtharr


def aprime(index ,quadrant=1, position = 1, plane=2):
    theta = math.pi /3 
    y = theta * (plane-1)* (1 + 6*index)
    if quadrant == 1:  
        y = math.sqrt((y/theta)**2 - 0.25)
        y = math.floor(y)
    elif quadrant == 4:
        y = theta* (plane-1)* 5 *(1 + (6/5)*index)
        y = math.sqrt((y/theta)-0.25)    
    else:
        return "Quadrant must be in the 1st or 4th please enter 1 or 4 and re-run "
        
    if(math.floor(y) % 2 != 0):
        y = math.floor(y)
        y = y + 1
    if(type(y) != 'int'):
        y = math.floor(y)    
    if position == 1:
        y = y + 1
    elif position == -1:
        y = y - 1
    else:
        return "position must be 1 or -1 (+1,-1) for super or sub"
    
    return y
    
        
        
    
        
        
    
     
    