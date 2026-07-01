from database.record import Record


class Database:
    def connect(self):
        pass
    
    def execute(self, query, params):
        pass
    
    def save(self, obj: Record):
        pass
    
    def load(self, obj: Record):
        pass
    
    def delete(self, obj: Record):
        pass