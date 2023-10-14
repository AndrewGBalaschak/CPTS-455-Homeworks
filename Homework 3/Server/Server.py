import socket
import ssl
import os
import sys
sys.path.append('../Homework 3')
import File_Transfer
import Commands

# The host and port number to listen on
HOST = 'localhost'
PORT = 4949
# The size of the buffer for receiving data
BUFFER_SIZE = File_Transfer.BUFFER_SIZE

# Create SSL context
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile='Server\server.crt', keyfile='Server\server.key')

# Create a socket for listening 
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to an address and a port
listen_socket.bind((HOST, PORT))
# Listen for incoming connections
listen_socket.listen()
print(f'Server is listening on port {HOST}:{PORT}')

# Accept a connection from a client
server_socket, client_address = listen_socket.accept()
print(f'Server accepted a connection from {client_address}')

# Close the listening socket
listen_socket.close()

# Wrap the socket in a Secure Socket Layer
server_socket = context.wrap_socket(server_socket, server_side = True)

# Print help
Commands.help()

# Communicate with the client
running = True
while running:
    # RECEIVE MESSAGES
    # Receive an encrypted message from the client
    data = server_socket.recv(BUFFER_SIZE)
    if not data:
        print('Client closed the connection')
        break

    # Decode the message from bytes to a string
    message = data.decode()
    
    # Check if the message is for a file transfer
    if message.startswith("File:") or message.startswith("file:"):
        # Receive the file from the client
        print(f'Receiving the file: {message[5:]}')
        File_Transfer.receive_file(server_socket)
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
                server_socket.sendall(message.encode())

                # Send the file
                File_Transfer.send_file(server_socket, file_name)
                # Print a confirmation message
                print(f'Sent {file_name} to client.')
                sent = True
            else:
                # Print an error message if the file does not exist
                print(f'File {file_name} does not exist.')

        # Regular message
        else:
            # Send the message to the client
            server_socket.sendall(message.encode())
            sent = True

# Close the socket
server_socket.close()