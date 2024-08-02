from collections import OrderedDict

print("This is a Dict:\n")
d = {}
d['a'] = 100
d['b'] = 200
d['c'] = 300
d['d'] = 400

for key, value in d.items():
    print(key, value)

print("\nThis is an ordered Dict\n")
od = OrderedDict()

od['a'] = 100
od['b'] = 200
od['c'] = 300
od['d'] = 400

for key, value in od.items():
    print(key, value)
print(od)
