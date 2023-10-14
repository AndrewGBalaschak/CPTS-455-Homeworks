import socket
import ssl
import os
import sys
import threading
sys.path.append('../Homework 3')
import File_Transfer
import Commands

# The host and port number to connect to
HOST = 'localhost'
PORT = 4949 
# The size of the buffer for receiving data
BUFFER_SIZE = File_Transfer.BUFFER_SIZE

# Create SSL context
context = ssl.create_default_context()
context.load_verify_locations('Server\server.crt')
context.check_hostname = True
context.verify_mode = ssl.CERT_REQUIRED

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Try connecting to the server
try:
    client_socket.connect((HOST, PORT))
    print(f'Client connected to {HOST}:{PORT}')
except:
    print("Server refused to connect.")
    sys.exit()

# Wrap the socket in a Secure Socket Layer
client_socket = context.wrap_socket(client_socket, server_side = False, server_hostname = HOST)

# Print help
Commands.help()

# Communicate with the server
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
            Commands.help()

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
                client_socket.sendall(message.encode())

                # Send the file
                File_Transfer.send_file(client_socket, file_path)

                # Print a confirmation message
                print(f'Sent {basename} to {HOST}:{PORT}')
                sent = True
            else:
                # Print an error message if the file does not exist
                print(f'File {file_path} does not exist.')

        # Regular message
        else:
            # Send the message to the server
            client_socket.sendall(message.encode())
            sent = True


    # RECEIVE MESSAGES
    # Receive an encrypted message from the server
    data = client_socket.recv(BUFFER_SIZE)
    if not data:
        print('Server closed the connection')
        running = False
        break

    # Decrypt the message from bytes to string
    message = data.decode()

    # Check if the message is a file name
    if message.startswith("File:") or message.startswith("file:"):
        # Receive the file from the server
        print(f'Receiving the file: {message[5:]}')
        File_Transfer.receive_file(client_socket)
        print(f'Received the file: {message[5:]}')
        continue

    # Otherwise display the message as text
    else:
        print(f'Server: {message}')

# Close the socket
client_socket.close()