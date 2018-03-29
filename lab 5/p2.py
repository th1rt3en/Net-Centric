from random import randint
x = randint(1, 100)
print "Random number: %d - " % x + ("Even","Odd")[x%2]
