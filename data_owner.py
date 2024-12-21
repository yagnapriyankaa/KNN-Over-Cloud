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

# initializing positive security parameters
c = random.randint(1,10)
e = random.randint(1,10)
n = d+c+e+1
def mod(a,b):
    return a%b
def power_mod(base, exponent, modulus):
    result = 1
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent //= 2
    return result

#Helper Function to get a permutation function
def getPerm(n):

    perm = [i for i in range(n)]

    for i in range(n):

        j = random.randint(0, n - 1)
        while(j==i):
            j = random.randint(0,n-1)

        temp = perm[i]
        perm[i] = perm[j]
        perm[j] = temp


    return perm

#Helper function to get the inverse of the permutation function
def get_inverse_permutation(perm):
    n = len(perm)
    inverse_perm = [0] * n

    for i in range(n):
        inverse_perm[perm[i]] = i

    return inverse_perm

#Helper Function to generate invertible matrix M
def generateInvertibleMatrix(n):

    matrix = 1 + np.random.randint(4,size = (n,n)) #generates a nxn matrix with each element being an integer between 1 and 5

    # Check if the matrix is invertible
    while np.linalg.matrix_rank(matrix) < n:
        matrix = 1 + np.random.randint(4, size=(n, n))

    # Convert NumPy matrix to multidimensional list
    matrix_list = []
    for row in matrix:
        nested_list = list(row)
        matrix_list.append(nested_list)

    return matrix_list

#Obtains the dataset from database.txt
def getD():
    D = []
    f = open("database.txt", "r")
    for x in f:
        row = [int(num) for num in x.strip().split()]
        D.append(row)

    #We must apply shifting to make sure that no negative values are a part of our database
    for i in range(m):
        for j in range(d):
            if D[i][j]<0:
                D[i][j] = abs(D[i][j])+10000

    return D

#generates the private key of the Data Owner
def KeyGen():

    # generating a random invertible matrix of dimension nxn
    M = generateInvertibleMatrix(n)

    #generating random vectors as a part of our private key
    S = [random.random()*1000 for _ in range(d+1)]
    t = [random.random()*1000 for _ in range(c)]

    #generating a permutation function perm of n numbers
    perm = getPerm(n)

    return [S,t,perm,M]

#encrypts single data point
def computeEncryptedDatapoint(D,i,Key,v):
    p = D[i]
    mag_p_2 = 0
    for i in p:
        mag_p_2 += i*i

    S = Key[0]
    t = Key[1]
    perm = Key[2]
    M = Key[3]

    p_intermediate = []
    p_encrypted = [0 for i in range(n)]

    #calculating p_intermediate which is p_encrypted before permutation and multiplication by M_inv
    for i in range(d):
        p_intermediate.append(S[i] - 2*p[i])

    p_intermediate.append(S[d]+mag_p_2)

    for i in t:
        p_intermediate.append(i)

    for i in v:
        p_intermediate.append(i)

    #permutation
    c = 0
    for element in p_intermediate:
        p_encrypted[perm[c]] = element
        c+=1

    p_encrypted = np.array(p_encrypted)
    p_encrypted = p_encrypted.reshape(1,-1)

    M = np.array(M)
    M = M.reshape(n,n)

    M_inv = np.linalg.inv(M)

    p_encrypted = np.matmul(p_encrypted,M_inv)
    p_encrypted = p_encrypted.tolist()

    return p_encrypted[0] #this returns p_encrypted as a normal python list

#encrypts the whole database
def encryptData(D,Key):

    D_encrypted = []
    for i in range(m):
        v = [random.random() * 1000 for _ in range(e)]

        p_enc_i = computeEncryptedDatapoint(D, i, Key, v)

        D_encrypted.append(p_enc_i)

    return D_encrypted

#we set up this function to be able to send large database across sockets
def send_data(socket, data, buffer_size):
    total_sent = 0
    while total_sent < len(data):
        chunk = data[total_sent:total_sent + buffer_size]
        total_sent += socket.send(chunk)

#Send the encrypted database to cloud server
def sendD_encrypted(D_encrypted):
    dataOwner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creates the data owner socket
    dataOwner.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  # a useful line in debugging to prevent OSError: [Errno 98] Address already in use
    dataOwner.bind(ADDR1)

    dataOwner.connect(ADDR2)
    print(f"[DATA OWNER]Connected to Cloud Server at {ADDR2}")

    send_data(dataOwner, json.dumps(D_encrypted).encode(), 4096) #set the buffer size as 4096

    print(f"[DATA OWNER]Sent encrypted database to Cloud Server")

    dataOwner.close()
    print(f"[DATA OWNER]Closed connection")

#Receive Encrypt and Send encrypted query to and from Query User with modifications. ONE TIME FUNCTION NEED TO INC. RE-USABILITY
def queryRES(Key):
    dataOwner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creates the data owner socket
    dataOwner.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # a useful line in debugging to prevent OSError: [Errno 98] Address already in use
    dataOwner.bind(ADDR1)
    dataOwner.listen()
    print(f"[DATA OWNER]Data Owner is listening on {ADDR1}")

    # creating this loop allows the data owner to interact with multiple clients in sequential order
    while True:
        conn, addr = dataOwner.accept()  # starts a connection between client and data owner
        print(f"[DATA OWNER]{addr} connected. ")

        connected = True
        while connected:
            message= json.loads(conn.recv(32768).decode())  # message obtained and converted to a list
            public_key = message[0]
            query_encrypted = message[1]
            print("[Data Owner]Obtained message and deconstructed it successfully")

            #computations
            A_q = queryEncrypt(query_encrypted,Key,public_key)

            print(f"[Data Owner]Successfully computed A_q")

            conn.sendall(json.dumps(A_q).encode())

            print("[Data Owner]Sent the encrypted query back to the query user")
            dataOwner.close()
            connected = False

        print(f"[DATA OWNER]{addr} has disconnected.")
        break

#Paillier Encryption Function needed while calculating A_q
def encrypt(public_key, plaintext):

    n = public_key[0]
    g = public_key[1]

    # random number in {1,2,3,...,n-1}
    r = random.randint(1, n - 1)

    if (plaintext >= int(n)):
        raise ValueError("Invalid Message! Please try again with a smaller message.")
    else:
        ciphertext = int(mod(power_mod(g, int(plaintext), int(n ** 2)) * power_mod(r, int(n), int(n ** 2)), int(n ** 2)))

        return ciphertext

#Query Modification
def queryEncrypt(query_encrypted,Key,public_key):
    #checks if the query is valid
    if(len(query_encrypted)!=d):
        return False

    #get necessary parameters
    perm = Key[2]
    #create inverse permutation list
    inverse_perm = get_inverse_permutation(perm)

    M = Key[3]
    c = len(Key[1])
    R_q = [1+int(random.random()*99) for i in range(c)] #c-dimensional random vector having integers between 1 and 100
    beta_q =1+int(random.random()*99) # random positive integer between 1 and 100
    A_q = [0 for i in range(n)]

    #To convert n and g to normal integers
    public_key[0] = int(public_key[0])
    public_key[1] = int(public_key[1])

    #compute n-dimensional encrypted vector A_q
    for i in range(n):
        A_q[i] = int(encrypt(public_key,0))

        for j in range(n):
            t = inverse_perm[j]

            if t < d:
                phi = int(beta_q) * int(M[i][j])
                A_q[i] = int(mod(A_q[i] * int(query_encrypted[t])**phi,int(public_key[0]**2)))

            elif t == d:
                phi = int(beta_q) * int(M[i][j])
                A_q[i] = int(mod(A_q[i] * int(encrypt(public_key,phi)),int(public_key[0]**2)))

            elif t < d+c+1:
                w = t-d-1
                phi = int(beta_q) * int(M[i][j]) * int(R_q[w]) #1 to 125
                A_q[i] = int(mod(A_q[i] * int(encrypt(public_key,phi)),int(public_key[0]**2)))

    return A_q

#___________________________________________________________________________________________________________________

#Obtain the database
D = getD()
print("[Data Owner]Obtained the database")

#Generate the private Key
Key = KeyGen()
print("[Data Owner]Generated its private key")

#Encrypt the data using the private Key
D_encrypted = encryptData(D,Key)
print("[Data Owner]Encrypted its data using the private key")

#Send the encrypted database to the cloud server
sendD_encrypted(D_encrypted)

#Obtain the encrypted query from the Query User, perform necessary modification and send it back to the Query User - Receive, Encrypt and Send
queryRES(Key)

