from database.record import Record
from database.sqlite_database import SqliteDatabase

class TestRecord(Record):
    def __init__(self):
        super().__init__('Test Record')
        self.value = 'Test Value'
        
db = SqliteDatabase('test.db')

db.connect()
db.hard_reset()

record = TestRecord()

print(f'Record: {record}')
print(f'Name: {record.name}')
print(f'Value: {record.value}')

print('--------------------')

db.save(record)

record: TestRecord = db.load('Test Record')

print(f'Record: {record}')
print(f'Name: {record.name}')
print(f'Value: {record.value}')

db.disconnect()