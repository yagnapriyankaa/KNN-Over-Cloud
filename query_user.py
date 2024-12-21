import random
import socket
import json
import sage
import numpy as np
import math
from sympy import randprime

#common parameters for the simulation
d = 50
m = 10000

#socket information
PORT1 = 65432  # data owner port
PORT2 = 65433  # cloud server port
SERVER = socket.gethostname()
ADDR1 = (SERVER, PORT1)  # data owner
ADDR2 = (SERVER, PORT2)  # cloud server
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
def inverse_mod(a,m):
    return pow(a,-1,m)

#Paillier class in order to perform homomorphic encryption of the Query
class Paillier:

    def __init__(self,k = 1024):
        self.k = k
        #useful function
        def L(x,n):
            return (x-1)//n #note this is floor division in order to avoid overflow error

        while(True):
            #two distinct primes such that gcd(pq,(p-1)(q-1)) = 1
            self.p = int(randprime(2,2**self.k))
            while(True):
                self.q = int(randprime(2,2**self.k))
                if(self.p==self.q or math.gcd(self.p*self.q,(self.p-1)*(self.q-1)) != 1):continue
                else:break
            #computes n=pq
            self.n = self.p*self.q
            #computes lambda = lcm(p-1,q-1) ---> private key
            self.l = math.lcm(self.p-1,self.q-1)
            #computes g=random number in {1,2,3,..n^2-1}
            self.g = random.randint(1,self.n**2-1)
            while(math.gcd(self.g,self.n)!=1):
                self.g = random.randint(1, self.n ** 2 - 1)

            #computes mu - modular multiplicative inverse
            if(math.gcd(L(int(power_mod(self.g,self.l,self.n**2)),self.n),self.n)==1):
                self.mu = inverse_mod(int(L(int(power_mod(self.g,self.l,self.n**2)),self.n)),self.n)
                break
            else:
                continue



    def get_public_key(self):
        return self.n,self.g

    def encrypt(self,plaintext):

        # random number in {1,2,3,...,n-1}
        self.r = random.randint(1, self.n - 1)

        if(plaintext >= int(self.n)):
            raise ValueError("Invalid Message! Please try again with a smaller message.")
        else:
            ciphertext = int(mod(power_mod(self.g, plaintext, self.n ** 2) * power_mod(self.r,self.n,self.n ** 2),self.n ** 2))

            return ciphertext

    def decrypt(self,ciphertext):
        # useful function
        def L(x, n):
            return (x - 1) // n #note this is floor division in order to avoid overflow error

        if(ciphertext>=self.n**2):
            raise ValueError("Invalid Message! Please try again with a smaller message.")

        #else:
        pm = power_mod(int(ciphertext),self.l,self.n*self.n)
        L_val = L(pm,self.n)
        plaintext = int(mod(int(L_val)*self.mu,self.n))
        return plaintext

#function that sends the encrypted query to the data owner and obtains A_q - Collaborative encryption scheme for query
def sendAndReceiveQuerywithKey(message):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # initializes the client object
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  # a useful line in debugging to prevent OSError: [Errno 98] Address already in use

    # interaction with the data owner

    client.connect(ADDR1)  # establishes connection with the data owner's port
    client.sendall(json.dumps(message).encode())  # sends the query to the data owner for modification
    print("[Query User]Sent the encrypted query - E_pk(q)")

    A_q = json.loads(client.recv(32768).decode())

    print("[Query User]Received A_q")

    client.close()  # closes the connection with the data owner

    return A_q

#function that sends q_dash to the Cloud Server and receives back the index set after k-NN computation
def sendAndReceiveIndexSet(q_dash):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # initializes the client object
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)  # a useful line in debugging to prevent OSError: [Errno 98] Address already in use

    # interaction with the cloud server
    client.connect(ADDR2)  # establishes connection with the cloud server's port

    client.sendall(json.dumps(q_dash).encode())
    print("[Query User]Sent the encrypted query - q_dash")

    index_set = json.loads(client.recv(32768).decode())
    client.close()

    return index_set

#function to stream large amount of data in chunks
def send_data(socket, data, buffer_size):
    total_sent = 0
    while total_sent < len(data):
        chunk = data[total_sent:total_sent + buffer_size]
        total_sent += socket.send(chunk)


#generate a query - This can be taken as input from user - for now we initialize it to an arbitrary placeholder value
#q = [random.randint(-10000, 10000) for _ in range(d)]
q = [2102, 9253, -5196, -7513, -333, -962, -4486, 6424, 7521 ,9353 ,2475, -7396, -7381, -8905, 5984, 3675 ,4310, -8795 ,680, -6550, -1604, 4352, 6142, -5122 ,1890, 8351, -9716 ,3934 ,139, 2766 ,-3235 ,3406 ,5233 ,-3624, -7196, 7671, 9281 ,1703, 8131, -1119, -4485, -4919 ,3106 ,-1763 ,-343 ,-1255 ,241 ,2234 ,-2793 ,-6850]
#we set the query as the first point in the database, so we expect the index set to be [0] for k=1

print("[Query User]Generated random query")

#We apply shifting here as well to eliminate the negative values
for i in range(d):
    if q[i] < 0:
        q[i] = abs(q[i]) + 10000

#Generate public key and private key of Homomorphic Crypto-system
paillier = Paillier(k=16)

public_key = paillier.get_public_key()

#encrypt the query point to send to the Data Owner
q_cipher = [paillier.encrypt(x) for x in q]
print(f"[Query User]Encrypted the query ")

#we want to send both the public key and the q_cipher to the data owner so that he can generate A_q
message = [public_key,q_cipher]

#Send the encrypted query point to the Data Owner
A_q = sendAndReceiveQuerywithKey(message)

#Now decrypts using the secret paillier key
q_dash = [paillier.decrypt(x) for x in A_q]
print("[Query User]Computed q_dash")

#Send q_dash to the cloud server and receive the index set after k-NN computation
index_set = sendAndReceiveIndexSet(q_dash)

print(f"Index Set : {index_set}")