from collections import namedtuple

# Define a namedtuple type 'Interval' with fields 'start' and 'end'
Interval = namedtuple("Interval", ["start", "end"])

# Create an instance of Interval
interval = Interval(start=1, end=5)

# Iterate over the field names
for field_name in interval._fields:
    print(f"{field_name}: ", getattr(interval, field_name))


a = isinstance(interval, Interval)
b = isinstance(interval, tuple)
print("e")
