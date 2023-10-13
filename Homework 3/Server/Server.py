import socket
import os
from cryptography.fernet import Fernet
import sys
sys.path.append('../Homework 3')
import File_Transfer
import Commands

# The port number to listen on
PORT = 4949
# The size of the buffer for receiving data
BUFFER_SIZE = File_Transfer.BUFFER_SIZE


# Create a socket for listening
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to an address and a port
listen_socket.bind(('', PORT))
# Listen for incoming connections
listen_socket.listen()
print(f'Server is listening on port {PORT}')

# Accept a connection from a client
client_socket, client_address = listen_socket.accept()
print(f'Server accepted a connection from {client_address}')

# Close the listening socket
listen_socket.close()

# Generate a new encryption key for this session and send it to the client
key = Fernet.generate_key()
client_socket.sendall(key)

# Print help
Commands.help()

# Communicate with the client using the key
running = True
while running:
    # RECEIVE MESSAGES
    # Receive an encrypted message from the client
    encrypted_data = client_socket.recv(BUFFER_SIZE)
    if not encrypted_data:
        print('Client closed the connection')
        break

    # Decrypt the message from bytes to string using the key
    message = Fernet(key).decrypt(encrypted_data).decode()
    
    # Check if the message is a file name
    if message.startswith("File:") or message.startswith("file:"):
        # Receive the file from the client using the key
        print(f'Receiving the file: {message[5:]}')
        File_Transfer.receive_file(client_socket, key)
        print(f'Received the file: {message[5:]}')
        continue
    
    # Otherwise, display the message as text
    else:
        print(f'Client: {message}')

    # SEND MESSAGES
    sent = False
    while not sent:
        # Get a message from the user
        message = input('Server: ')

        # Check if the message is the quit command
        if message == 'q':
            running = False
            break

        # Check if the message is the help command
        elif message == 'help':
            Commands.help()

        # Check if the message is a file name
        elif message.startswith("File:") or message.startswith("file:"):
            # Get the filename
            file_name = message[5:]

            # Make sure file exists
            if os.path.isfile(file_name):
                # Tell the client we are sending a file
                encrypted_data = Fernet(key).encrypt(message.encode())
                client_socket.sendall(encrypted_data)

                # Send the file
                File_Transfer.send_file(client_socket, file_name, key)
                # Print a confirmation message
                print(f'Sent {file_name} to client.')
                sent = True
            else:
                # Print an error message if the file does not exist
                print(f'File {file_name} does not exist.')

        # Regular message
        else:
            # Encode and encrypt the message from string to bytes using the key
            encrypted_data = Fernet(key).encrypt(message.encode())
            # Send the encrypted message to the server using the key
            client_socket.sendall(encrypted_data)
            sent = True

# Close the socket
client_socket.close()