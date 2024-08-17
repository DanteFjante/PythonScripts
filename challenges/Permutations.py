'''
this code shows number of possible permutations for a number of known values where the order is unknown

for 1, 2, 3, 4 the P (permutations) is 24
and D (distinct) is 24
which is the number of values factorial
(1 × 2 × 3 × 4)

for 1, 2, 3, 3 where two values are the same
the D is number of factorial divided by 2
(1×3×4)
for 1, 2, 3, 3, 3
P is 120 and D is 20 so it is 5 factorial divided by 2 then 3
(1×4×5)
for 1, 2, 2, 3, 3 the P is 120 and D is 30
so its 5 factorial divided by 2 then 2 again
(1×3×4×5÷2)

The solution is C (count) = number of values in the sequence
divided by the factorial of the number of occurences in the sequence for each distict value in the sequence
'''

#playground
numbers = [1, 2, 2, 3, 3, 3, 6, 5, 6, 1]

 
# code  
def existsInList(li, item):
    if not li:
        return False
    for i in li:
        if i == item:
            return True
    return False

def factorial(nr):
    res = 1
    for i in range(1, nr+1):
        res *= i
    return res

def getAllRef(li, curr, retlist):
    cp = li.copy()
    for i in curr: 
        cp.remove(i)
    if not cp:
        return
    for i in cp:
        cp2 = curr.copy()
        cp2.append(i)
        getAllRef(li, cp2, retlist)
        if(len(cp2) == len(li)):
            retlist.append(cp2)

def getUniquesRef(li, retlist):
    for i in li:
        if existsInList(retlist, i):
            continue
        retlist.append(i)
          
def getNrOfOccurencesRef(li, retlist):
    uniques = []
    getUniquesRef(li, uniques)
    for i in uniques:
        count = li.count(i)
        retlist.append(count)

def getDivisorsRef(li, retlist):
    for i in li:
        fact = factorial(i)
        retlist.append(fact)

def getNrPermutations(li):
    fact = factorial(len(li))
    occurences = []
    dividers = []
    getNrOfOccurencesRef(li, occurences)
    getDivisorsRef(occurences, dividers)
    for i in dividers:
        fact /= i
    return fact

#Result
print("Fast: " + str(getNrPermutations(numbers)))



#Assertion
'''
newlist = []
distinct = []
getAllRef(numbers, [], newlist)
getUniquesRef(newlist, distinct)

print("Permutations: " + str(len(newlist)))
print("Distinct: " + str(len(distinct)))

for dist in distinct:
    print(dist)
 '''