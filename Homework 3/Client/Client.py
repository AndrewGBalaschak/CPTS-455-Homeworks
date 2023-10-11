import socket
import os
from cryptography.fernet import Fernet
import sys
sys.path.append('../Homework 3')
import File_Transfer

# The server address and port number to connect to
SERVER_ADDRESS = '127.0.0.1' 
PORT = 4949 
# The size of the buffer for receiving data
BUFFER_SIZE = File_Transfer.BUFFER_SIZE

# Create a socket for connecting
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the server
server_socket.connect((SERVER_ADDRESS, PORT))
print(f'Client connected to {SERVER_ADDRESS}:{PORT}')

# Receive a new encryption key from the server for this session
key = server_socket.recv(BUFFER_SIZE)

def help():
    print("Type a message and press [Enter] to send.")
    print("Type [File:FileName] to send a file")
    print("Type [q] to quit")

# Print help
help()

# Communicate with the server using the key
running = True
while running:
    # SEND MESSAGES
    sent = False
    while not sent:
        # Get a message from the user
        message = input('Client: ')

        # Check if the message is the quit command
        if message == 'q':
            running = False
            break

        # Check if the message is the help command
        elif message == 'help':
            help()

        # Check if the message is a file name
        elif message.startswith("File:") or message.startswith("file:"):
            # Get the filename and path
            basename = message[5:]
            file_path = os.getcwd()
            file_path = os.path.join(file_path, "Client")
            file_path = os.path.join(file_path, basename)

            # Make sure file exists
            if os.path.isfile(file_path):
                # Tell the server we are sending a file
                encrypted_data = Fernet(key).encrypt(message.encode())
                server_socket.sendall(encrypted_data)

                # Send the file
                File_Transfer.send_file(server_socket, file_path, key)
                # Print a confirmation message
                print(f'Sent {basename} to {SERVER_ADDRESS}:{PORT}')
                sent = True
            else:
                # Print an error message if the file does not exist
                print(f'File {file_path} does not exist.')

        # Regular message
        else:
            # Encode and encrypt the message from string to bytes using the key
            encrypted_data = Fernet(key).encrypt(message.encode())
            # Send the encrypted message to the server using the key
            server_socket.sendall(encrypted_data)
            sent = True


    # RECEIVE MESSAGES
    # Receive an encrypted message from the server using the key
    encrypted_data = server_socket.recv(BUFFER_SIZE)
    if not encrypted_data:
        print('Server closed the connection')
        running = False
        break

    # Decrypt the message from bytes to string using the key
    message = Fernet(key).decrypt(encrypted_data).decode()

    # Check if the message is a file name
    if message.startswith("File:") or message.startswith("file:"):
        # Receive the file from the server using the key
        print(f'Receiving the file: {message[5:]}')
        File_Transfer.receive_file(server_socket, key)
        print(f'Received the file: {message[5:]}')
        continue

    # Otherwise display the message as text
    else:
        print(f'Server: {message}')

# Close the socket
server_socket.close()