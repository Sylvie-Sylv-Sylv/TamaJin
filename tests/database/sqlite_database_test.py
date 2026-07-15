from database.record import Record
from database.sqlite_database import SqliteDatabase

class MockRecord(Record):
    def __init__(self):
        super().__init__('Test Record')
        self.value = 'Test Value'
        
db = SqliteDatabase('test.db')

db.connect()
db.hard_reset()

record = MockRecord()

print(f'Record: {record}')
print(f'Name: {record.name}')
print(f'Value: {record.value}')

print('--------------------')

db.save(record)

record: MockRecord = db.load('Test Record')

print(f'Record: {record}')
print(f'Name: {record.name}')
print(f'Value: {record.value}')

db.disconnect()