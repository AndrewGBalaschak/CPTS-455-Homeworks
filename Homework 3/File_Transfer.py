import socket
import os
import hashlib
from cryptography.fernet import Fernet
BUFFER_SIZE = 1024

# Send a file over a socket
def send_file(socket, file_path, key):
    # Create a Fernet object with the given key
    f = Fernet(key)

    # Get the file size and the file name
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    # Send the file size and the file name to the socket
    socket.sendall(str(file_size).encode() + b':' + file_name.encode() + b':')

    # Open the file in binary mode
    with open(file_path, 'rb') as f_in:
        # Read the file contents
        data = f_in.read()

        # Encrypt the file contents
        encrypted_data = f.encrypt(data)

        # Compute the checksum of the encrypted data using SHA256
        checksum = hashlib.sha256(encrypted_data).hexdigest()
        print(f"Sent checksum: {checksum}")

        # Send the checksum to the socket
        socket.sendall(checksum.encode() + b':')

        # Send the encrypted data to the socket
        socket.sendall(encrypted_data)

    # Close the file
    f_in.close()

# Receive a file from a socket
def receive_file(socket, key):
    # Create a Fernet object with the given key
    f = Fernet(key)

    # Receive the file size and the file name from the socket
    data = socket.recv(BUFFER_SIZE).decode()
    print(f"Data: {data}")
    split = data.split(':')
    file_size = int(split[0])
    file_name = split[1]

    print(f"Size: {file_size} bytes")
    print(f"Name: {file_name}")

    # Receive the checksum from the socket
    checksum = socket.recv(BUFFER_SIZE).decode()
    checksum = checksum.split(':')[0]
    print(f"Received checksum:{checksum}")

    # Write the (still encrypted) file in binary mode
    with open(file_name + '.enc', 'wb') as f_out:
        # Initialize a variable to store the received data size
        received_size = 0
        print("File open success")

        # Loop until all the data is received
        while received_size < file_size:
            # Receive a chunk of data from the socket
            data = socket.recv(BUFFER_SIZE)

            # Update the received data size
            received_size += len(data)

            # Write the data to the file
            f_out.write(data)

        # Close the file
        f_out.close()

    # Open the encrypted file in binary mode
    with open(file_name + '.enc', 'rb') as f_in:
        # Read the file contents
        encrypted_data = f_in.read()

        # Decrypt the file contents
        decrypted_data = f.decrypt(encrypted_data)

        # Compute the checksum of the encrypted data using SHA256
        computed_checksum = hashlib.sha256(encrypted_data).hexdigest()

        # Compare the computed checksum with the received checksum
        if computed_checksum == checksum:
            # If they match, write the decrypted data to a new file without .enc extension
            with open(file_name, 'wb') as f_dec:
                f_dec.write(decrypted_data)
                print(f"File {file_name} received and decrypted successfully.")
                print(f"Saved as {file_name}.dec")
                f_dec.close()

                # Delete the encrypted file
                # os.remove(file_name + '.enc')
        
        else:
            # If they don't match, print an error message and delete the file
            print(f"File {file_name} corrupted during transmission.")
            print(f"Checksum mismatch: {computed_checksum} != {checksum}")
            os.remove(file_name + '.enc')
    
    # Close the file
    f_in.close()