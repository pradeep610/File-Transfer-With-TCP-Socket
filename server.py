 
from ast import For
import socket
import sys
import time
import os
import struct

#from client import FORMAT

print("\nWelcome to the FTP server.\n\nTo get started, connect a client.")

# Initialise socket stuff
TCP_IP = "127.0.0.1" # Only a local server
TCP_PORT = 1456 # Just a random choice
BUFFER_SIZE = 1024 # Standard size
ADDR = (TCP_IP,TCP_PORT)
FORMAT = "utf-8"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(ADDR)
s.listen()
conn, addr = s.accept()

print("\nConnected to by address: {}".format(addr))

def upld():
    # Send message once server is ready to recieve file details
   # conn.send("1".encocode("utf-8"))
    # Recieve file name length, then file name
    #file_name_size = struct.unpack("h", conn.recv(2))[0]
    file_name = conn.recv(BUFFER_SIZE).decode(FORMAT)
    print("{}".format(file_name))
    # Send message to let client know server is ready for document content
    conn.send("1".encode(FORMAT))
    # Recieve file size
    file_size = struct.unpack("i", conn.recv(4))[0]
    # Initialise and enter loop to recive file content
    print("\nfile size:{}".format(file_size))
    start_time = time.time()
    output_file = open(file_name, "w")
    # This keeps track of how many bytes we have recieved, so we know when to stop the loop
    bytes_recieved = 0
    print("\nRecieving...")
    while bytes_recieved < file_size:
        l = conn.recv(BUFFER_SIZE).decode(FORMAT)
        output_file.write(l)
        bytes_recieved += BUFFER_SIZE
    # data = conn.recv(BUFFER_SIZE).decode(FORMAT)
    # output_file.write(data)
    output_file.close()
    print("\nRecieved file: {}".format(file_name))
    # Send upload performance details
    #conn.send((time.time() - start_time).encode(FORMAT))
    #print("Time taken to upload is :"time.time()-start_time)
    conn.send(struct.pack("f", time.time() - start_time))
   # conn.send(struct.pack("i", file_size))
    return

def list_files():
    print("Listing files...")
    # Get list of files in directory
    listing = os.listdir(os.getcwd())
    # Send over the number of files, so the client knows what to expect (and avoid some errors)
    conn.send(struct.pack("i", len(listing)))
    total_directory_size = 0
    # Send over the file names and sizes whilst totaling the directory size
    for i in listing:
        # File name size
        conn.send(struct.pack("i", sys.getsizeof(i)))
        # File name
        conn.send(i.encode(FORMAT))
        # File content size
        conn.send(struct.pack("i", os.path.getsize(i)))
        total_directory_size += os.path.getsize(i)
        # Make sure that the client and server are syncronised
        conn.recv(BUFFER_SIZE).decode(FORMAT)
    # Sum of file sizes in directory
    conn.send(struct.pack("i", total_directory_size))
    #Final check
    conn.recv(BUFFER_SIZE).decode(FORMAT)
    print("Successfully sent file listing")
    return

def dwld():
    #conn.send("1".encode(FORMAT))
    file_name_length = struct.unpack("h", conn.recv(2))[0]
    # print(file_name_length)
    file_name = conn.recv(file_name_length).decode(FORMAT)
    print(file_name)
    if os.path.isfile(file_name):
        # Then the file exists, and send file size
        conn.send(struct.pack("i", os.path.getsize(file_name)))
    else:
        # Then the file doesn't exist, and send error code
        print("File name not valid")
        conn.send(struct.pack("i", -1))
        return
    # Wait for ok to send file
    conn.recv(BUFFER_SIZE).decode(FORMAT)
    # Enter loop to send file
    start_time = time.time()
    print("Sending file...")
    content = open(file_name, "r")
    #data = content.read()
    # Again, break into chunks defined by BUFFER_SIZE
    l = content.read(BUFFER_SIZE)
    while l:
        conn.send(l.encode(FORMAT))
        l = content.read(BUFFER_SIZE)
    #conqun.send(data.encode(FORMAT))
    content.close()
    # Get client go-ahead, then send download details
    conn.recv(BUFFER_SIZE).decode(FORMAT)
    conn.send(struct.pack("f", time.time() - start_time))
    return


def delf():
    # Send go-ahead
    #conn.send("1".encode(FORMAT))
    # Get file details
    file_name_length = struct.unpack("h", conn.recv(2))[0]
    file_name = conn.recv(file_name_length).decode(FORMAT)
    # Check file exists
    if os.path.isfile(file_name):
        conn.send(struct.pack("i", 1))
    else:
        # Then the file doesn't exist
        conn.send(struct.pack("i", -1))
        return
    # Wait for deletion conformation
    confirm_delete = conn.recv(BUFFER_SIZE).decode(FORMAT)
    if confirm_delete == "Y":
        try:
            # Delete file
            os.remove(file_name)
            print("Successfully deleted the file")
            conn.send(struct.pack("i", 1))
        except:
            # Unable to delete file
            print("Failed to delete {}".format(file_name))
            conn.send(struct.pack("i", -1))
            
    else:
        # User abandoned deletion
        # The server probably recieved "N", but else used as a safety catch-all
        print("Delete abandoned by client!")
        return


def quit():
    # Send quit conformation
    conn.send("1".encode(FORMAT))
    # Close and restart the server
    conn.close()
    s.close()
    os.execl(sys.executable, sys.executable, *sys.argv)

while True:
    # Enter into a while loop to recieve commands from client
    print("\n\nWaiting for instruction")
    data = conn.recv(10).decode(FORMAT)
    # print("\nRecieved instruction: {}".format(data))
    #data ="LIST"
    # Check the command and respond correctly
    if data == "UPLD":
        upld()
    elif data == "LIST":
        list_files()
    elif data == "DWLD":
        dwld()
    elif data == "DELF":
        delf()
    elif data == "QUIT":
        quit()
    else:
        print("dataghjk")
    # Reset the data to loop
    data = None
