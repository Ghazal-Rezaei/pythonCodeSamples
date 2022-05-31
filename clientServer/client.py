import socket
import os
import pyaes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from hashlib import md5

server = '127.0.0.1'
port = 10001
KEY_LEN = 2048
SIGN_LEN = 256

AES_KEY_LEN = 32
IV_LEN = 16
AES_key = get_random_bytes(AES_KEY_LEN)

keyPair = RSA.generate(KEY_LEN)
pubKey = keyPair.publickey()
decrypter = PKCS1_OAEP.new(keyPair)

globalhash = None
cnt = 0


def decryptMsg(cipherText):
    IV = cipherText[-IV_LEN:]
    decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(AES_key,iv=IV))
    PT = decrypter.feed(cipherText[:-IV_LEN])
    PT += decrypter.feed()
    return PT


def verifyFile(CT):
    global globalhash
    global cnt
    signature = CT[-SIGN_LEN:]
    receivedHash = decrypter.decrypt(signature)
    if cnt == 0:
        PT = decryptMsg(CT[:-SIGN_LEN]).decode('utf-8')
        file = open(PT, 'rb').read()
        md5Hash = md5(file).hexdigest()
        if md5Hash == receivedHash.decode('utf-8'):
            print('\nsetting the hash value of the good code as the only acceptable md5 hash value.\n')
            cnt += 1
            globalhash = md5Hash
            return PT
    else:
        print('\nreceived a code with the same md5 hash value. Therefore, we\'re gonna execute it!\n')
        PT = decryptMsg(CT[:-SIGN_LEN]).decode('utf-8')
        file = open(PT, 'rb').read()
        md5Hash = md5(file).hexdigest()
        if md5Hash == globalhash and md5Hash == receivedHash.decode('utf-8'):
            return PT
    return "echo 'the file and its assigned signature do not match!'"


sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

print('connecting to the server...')
sock.connect((server,port))

print('receiving server\'s public key...')
server_pubKey = RSA.importKey(sock.recv(4096), passphrase=None)

print('sending client\'s public key to the server...')
sock.send(pubKey.exportKey(format='PEM', passphrase=None, pkcs=1))

print('sending client\'s AES key to the server...')
encrypter = PKCS1_OAEP.new(server_pubKey)
encrypted = encrypter.encrypt(AES_key)
sock.send(encrypted)

print('receiving the files...')
while True:
    CT = sock.recv(4096)
    if not CT:
        print('disconnecting...')
        break
    print('trying to execute the file sent by the server, provided that it is verified...')
    os.system(verifyFile(CT))
