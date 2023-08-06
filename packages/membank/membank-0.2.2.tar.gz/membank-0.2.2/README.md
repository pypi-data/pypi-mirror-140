# membank
Python library for storing data in persistent memory (sqlite, postgresql, berkeley db)
## usage
from membank import LoadMemory
from collections import namedtuple

memory = LoadMemory() # defaults to sqlite memory
Dog = namedtuple('Dog', ['color', 'size', 'breed'])
memory.create(Dog) # expects Python collections.namedtuple
memory.put.dog(Dog('brown')) # stores object into database
memory.get.dog() # retrieves first object found as namedtuple
dog = memory.get.dog()
assert dog.color == 'brown'

... new process ...
memory = LoadMemory() # this works unless sqlite memory is used before
dog = memory.get.dog()
assert dog.color == 'brown'
