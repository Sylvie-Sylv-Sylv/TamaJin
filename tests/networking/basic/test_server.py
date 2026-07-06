import socket
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../..", "src"))

from database.sqlite_database import SqliteDatabase
from diagnostics.levels import Level
from diagnostics.logger import Logger
from networking.server import Server
from networking.address_family import AddressFamily
from networking.protocol import Protocol
from tests.networking.basic.test_handlers import ReplyHandler
from networking.handlers.register_handler import RegisterHandler
from networking.handlers.login_handler import LoginHandler

logger = Logger()

logger.initialize(
    min_level = Level.DEBUG,
    console_output = True,
    use_colors = True
)

server = Server(
    AddressFamily.IPv4, Protocol.TCP,
    ('localhost', 8080),
    encoding = 'utf-8',
    database = SqliteDatabase('database.db')
)

server.add_handler(ReplyHandler)
server.add_handler(RegisterHandler)
server.add_handler(LoginHandler)

try:
    server.run(hard_reset_database = True, logger = logger)
    
    while not server.is_stopping.is_set():
        time.sleep(0.1)
except KeyboardInterrupt:
    server.stop(logger)