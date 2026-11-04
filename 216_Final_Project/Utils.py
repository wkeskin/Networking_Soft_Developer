# author : Narendra
# date   : November 22, 2021
#filename: wk12a_utils.py
#

#data format:
# id: 111
# time: 
# person: {
#  name: 'Narendra'
#  cell: '123-456-789'
# }
# core_temp: 98
# 
from random import randint
from time import asctime
from json import dumps

class Util:
    def __init__(self):
        self.start_id = 111
        self.temp = 37
        self.person = {'name':'Nataliia', 'cell': '(123)456-7890'}

    def get_json_data(self):
        self.start_id += 1
        self.temp += randint(-10, 10) /1000
        data = {'id': self.start_id, 'time': asctime(), 'core_temp': self.temp, 'person': self.person}
        return dumps(data, indent=2)

# gen = Util()
# for x in range(5):
#     print(gen.get_json_data())