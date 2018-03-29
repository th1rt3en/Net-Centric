import xml.etree.cElementTree as et
from Building import Building

print "Enter building ID:",
ID = raw_input()
print "Enter building floors:",
floor = raw_input()
print "Enter building address:",
add = raw_input()

b = Building(ID,floor,add)

print "ID: %s" % ID
print "Number of floors: %s" % floor
print "Address: %s" % add

tree = et.parse("test.xml")
data = tree.getroot()

et.SubElement(data, "building", ID=b.ID, numberOfFloors=b.floor, address=b.add).text = ""

tree.write("test.xml")
