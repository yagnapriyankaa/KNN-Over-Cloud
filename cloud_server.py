import random
import socket
import json
import numpy as np
import math
import sage

#common parameters for the simulation
d=50
m = 10000

#socket information
PORT1 = 65432  # data owner port
PORT2 = 65433  # cloud server port
SERVER = socket.gethostname()
ADDR1 = (SERVER, PORT1)  # data owner
ADDR2 = (SERVER, PORT2)  # cloud server

#function to receive the data in chunks
def receive_data(socket, buffer_size):
    received_data = b''
    while True:
        data_chunk = socket.recv(buffer_size)
        if not data_chunk:
            break
        received_data += data_chunk
    return received_data

#function to get the encrypted database from the Data Owner
def getD_encrypted():

    cloudServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creates the cloud server socket
    cloudServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  # a useful line in debugging to prevent OSError: [Errno 98] Address already in use
    cloudServer.bind(ADDR2)
    cloudServer.listen()
    print(f"[CLOUD SERVER]Cloud Server is listening on {ADDR2}")

    # Interaction with the Data Owner to obtain the encrypted database - D'
    while True:

        conn, addr = cloudServer.accept()
        print(f"[CLOUD SERVER]{addr} connected. ")

        connected = True
        while connected:

            D_encrypted = json.loads(receive_data(conn, 4096).decode()) #set the buffer size as 4096

            print("[CLOUD SERVER]Encrypted dataset - D' Received")

            connected = False

        cloudServer.close()
        print(f"[CLOUD SERVER]{addr} has disconnected.")
        break

    return D_encrypted

#Gets the encrypted query - q' from the query user and returns True if it manages to compute kNN successfully and send it back to the query user
def getQ_dash_kNNCompute(D_encrypted,k):

    cloudServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creates the cloud server socket
    cloudServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  # a useful line in debugging to prevent OSError: [Errno 98] Address already in use
    cloudServer.bind(ADDR2)
    cloudServer.listen()
    print(f"[CLOUD SERVER]Cloud Server is listening on {ADDR2}")

    # Interaction with the Query User to obtain the encrypted query - q_dash
    while True:

        conn, addr = cloudServer.accept()
        print(f"[CLOUD SERVER]{addr} connected. ")

        connected = True
        while connected:

            q_dash = json.loads(conn.recv(32768).decode())

            print("[CLOUD SERVER]Encrypted query - q_dash Received")

            index_set = kNNComp(D_encrypted,q_dash,k)

            conn.sendall(json.dumps(index_set).encode())

            connected = False

        cloudServer.close()
        print(f"[CLOUD SERVER]{addr} has disconnected.")
        break

    return True

#Gets the k-Nearest Neighbours of the query by comparing dot products of the encrypted query with each encrypted datapoint
def kNNComp(D_encrypted,q_dash,k):
    dot_product_set = []
    for i in range(len(D_encrypted)):
        dot_product_set.append(np.dot(np.array(D_encrypted[i]),np.array(q_dash)))

    indices = []  # To store the indices of the k lowest numbers

    for _ in range(k):
        min_index = -1
        for i in range(len(dot_product_set)):
            if i not in indices:  # Skip indices that are already found
                if min_index == -1 or dot_product_set[i] < dot_product_set[min_index]:
                    min_index = i
        indices.append(min_index)

    return indices

#___________________________________________________________________________________________________________________

#get the encrypted database from the data owner
D_encrypted = getD_encrypted()
print("[CLOUD SERVER]Obtained D_encrypted")

#Set k for kNN computation
k = 5

#get the encrypted query from the query user
if(getQ_dash_kNNCompute(D_encrypted, k)):
    print("[CLOUD SERVER]kNN Computation successful")

