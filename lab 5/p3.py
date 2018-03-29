import sys
h = int(sys.argv[1])
w = int(sys.argv[2])
print "Height: %d" % h
print "Width: %d" % w
print "*"*w
for _ in range(h-2): 
	print '*' + ' '*(w-2) + '*'
print "*"*w
