import socket
import os
import hashlib
BUFFER_SIZE = 1024

# Send a file over a socket
def send_file(socket, file_path):
    # Get the file size and the file name
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    # Send the file size and the file name to the socket
    socket.sendall(str(file_size).encode() + b":" + file_name.encode())

    # Open the file in binary mode
    with open(file_path, "rb") as f_in:
        # Read the file contents
        data = f_in.read()

        # Compute the checksum of the data using SHA256
        checksum = hashlib.sha256(data).hexdigest()

        # Send the checksum to the socket
        socket.sendall(checksum.encode())
        print(f"Sent checksum: {checksum}")

        # Send the encrypted data to the socket
        socket.sendall(data)

    # Close the file
    f_in.close()

# Receive a file from a socket
def receive_file(socket, file_path):
    # Receive the file size, file name, and checksum from the socket
    data = socket.recv(BUFFER_SIZE).decode()
    split = data.split(":")
    file_size = int(split[0])
    basename = split[1]
    checksum = socket.recv(BUFFER_SIZE).decode()
    print(f"Size: {file_size} bytes")
    print(f"Name: {basename}")
    print(f"Received checksum:{checksum}")

    # Put the file in the correct location
    # I know this is hacky but I just want it to work the way I want it to work
    file_path = os.path.join(file_path, basename)

    # Write the file in binary mode
    with open(file_path, "wb") as f_out:
        # Initialize a variable to store the received data size
        received_size = 0
        print("File open success.")

        # Loop until all the data is received and written
        while received_size < file_size:
            # Receive a chunk of data from the socket
            data = socket.recv(BUFFER_SIZE)

            # Update the received data size
            received_size += len(data)

            # Write the data to the file
            f_out.write(data)

        # Close the file
        f_out.close()

    # Open the file in binary mode
    with open(file_path, "rb") as f_in:
        # Read the file contents
        data = f_in.read()

        # Compute the checksum of the data using SHA256
        computed_checksum = hashlib.sha256(data).hexdigest()

        # Compare the computed checksum with the received checksum
        if computed_checksum == checksum:
            print(f"File {basename} received successfully.")
        
        # If they don"t match, print an error message and delete the file
        else:
            print(f"File {basename} corrupted during transmission.")
            print(f"Checksum mismatch: {computed_checksum} != {checksum}")

            # This part doesn"t work
            # os.remove(basename)
    
    # Close the file
    f_in.close()