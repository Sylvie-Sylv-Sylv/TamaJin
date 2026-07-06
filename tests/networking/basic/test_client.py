import socket
import sys
import os

from networking.user_record import UserRecord


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../..", "src"))

import time
import threading

from diagnostics.levels import Level
from diagnostics.logger import Logger
from networking.packet import Packet
from networking.client import Client
from networking.address_family import AddressFamily
from networking.protocol import Protocol
from tests.networking.basic.test_handlers import PrintReplyHandler, ReplyHandler
from networking.handlers.register_handler import RegisterHandler
from networking.handlers.login_handler import LoginHandler
from hashing.sha256 import SHA256


logger = Logger()

logger.initialize(
    min_level = Level.DEBUG,
    console_output = True,
    use_colors = True
)

dummy_record = UserRecord('guest', 'Guest', '')
client = Client(AddressFamily.IPv4, Protocol.TCP, UserRecord('testuser', 'Test User', 'password123'))

client.add_handler(PrintReplyHandler)

def run_mock_ui():
    """Runs the interactive command line interface.
    """
    time.sleep(0.5) 
    
    while not client.is_stopping.is_set():
        print("\n" + "="*40)
        print("          MOCK UI DASHBOARD")
        print("="*40)
        print("[1] Register a new account")
        print("[2] Login to an existing account")
        print("[3] Send a test message")
        print("[4] Disconnect and Exit")
        print("="*40)
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == '1':
            print("\n--- REGISTRATION ---")
            name = input("Enter a new username: ").strip()
            display_name = input("Enter your full name: ").strip()
            password = input("Enter a password: ").strip()
            
            record = UserRecord(name, display_name, password)
            
            try:
                Packet(RegisterHandler.id, record).send(client.sock)
                logger.info("Registration request sent.")
            except OSError as e:
                logger.error(f"Failed to send: {e}")
                
        elif choice == '2':
            print("\n--- LOGIN ---")
            name = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()
            
            record = UserRecord(name, "", password)
            
            try:
                Packet(LoginHandler.id, record).send(client.sock)
                logger.info("Login request sent.")
            except OSError as e:
                logger.error(f"Failed to send: {e}")

        elif choice == '3':
            print("\n--- SEND MESSAGE ---")
            msg = input("Type your message: ").strip()
            
            try:
                Packet(ReplyHandler.id, msg).send(client.sock)
                logger.info("Message sent.")
            except OSError as e:
                logger.error(f"Failed to send: {e}")

        elif choice == '4':
            print("Disconnecting...")
            client.is_stopping.set()
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
            
        time.sleep(1)


def wait_for_server(host, port):
    """Blocks and waits until a connection to the server can be established."""
    logger.info(f"Waiting for server to start at {host}:{port}...")
    
    while not client.is_stopping.is_set():
        try:
            # We use a raw socket just to test if the port is open
            with socket.create_connection((host, port), timeout=1):
                logger.info("Server detected! Initializing client...")
                return True
        except (OSError, ConnectionRefusedError):
            # Port is closed. Wait and try again.
            time.sleep(3)
            
    return False

try:
    if wait_for_server('localhost', 8080):
        
        client.connect(('localhost', 8080), logger)
        time.sleep(0.5) 
        
        client.handle(logger)
        
        run_mock_ui()

except KeyboardInterrupt:
    print("\nForce quitting...")
finally:
    client.is_stopping.set()
    client.stop(logger)