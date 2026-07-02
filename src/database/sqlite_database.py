import sqlite3
import os

from database.database import Database
from database.exceptions import NoRecordFoundError
from database.record import Record
from serialization.json_codec import JsonCodec
from serialization.obj_codec import ObjCodec

class SqliteDatabase(Database):
    def __init__(self, db_path: str):
        if not db_path.endswith('.db'):
            raise ValueError("Database path must end with '.db'")
        
        self.db_path = db_path
        self.connection = None
        
        self.is_initialized = False

    def connect(self):
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w'):
                pass
        self.connection = sqlite3.connect(self.db_path)
        
    def ensure_connection(self):
        if not self.connection:
            raise Exception("Database connection is not established.")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def initialize(self):
        self.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL
            )
        ''')
        
        self.is_initialized = True
    
    def reset(self):
        self.execute('DROP TABLE IF EXISTS records')
        self.initialize()
        
    def hard_reset(self):
        with open(self.db_path, 'w'):
            pass
        self.initialize()

    def execute(self, query, params = None):
        self.ensure_connection()
        
        cursor = self.connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        self.connection.commit()
        
        return cursor.fetchall()
    
    def save(self, obj: Record):
        self.ensure_connection()
        
        if not isinstance(obj, Record):
            raise TypeError("Object must be an instance of Record or its subclasses.")
        
        json_data = ObjCodec.encode(obj)
        name = json_data.pop('name', None)
        json_data = JsonCodec.obj_to_json(json_data)
        
        self.execute('INSERT INTO records (name, data) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET data = excluded.data;', (name, json_data))
    
    def load(self, name: str) -> Record:
        self.ensure_connection()
        
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        
        result = self.execute('SELECT name, data FROM records WHERE name = ?', (name,))
        
        if not result:
            raise NoRecordFoundError(name)
        
        name = result[0][0]
        json_data = result[0][1]
        obj_data = JsonCodec.json_to_obj(json_data)
        obj_data['name'] = name
        
        return ObjCodec.decode(obj_data)
    
    def delete(self, obj: Record):
        pass