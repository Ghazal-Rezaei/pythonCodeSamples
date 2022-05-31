import socket
import pyaes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from hashlib import md5

host = '127.0.0.1'
port = 10001
KEY_LEN = 2048

IV_LEN = 16

keyPair = RSA.generate(KEY_LEN)
pubKey = keyPair.publickey()
decrypter = PKCS1_OAEP.new(keyPair)

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind((host,port))
sock.listen(1)


def encryptMsg(plaintext,key):
    IV = get_random_bytes(IV_LEN)
    encrypter = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(key,iv=IV))
    CT = encrypter.feed(plaintext)
    CT += encrypter.feed()
    return CT+IV


con, addr = sock.accept()
print(str(addr[0]) + ':' + str(addr[1]), "connected")

print('sending server\'s public key...')
con.send(pubKey.exportKey(format='PEM', passphrase=None, pkcs=1))

print('receiving client\'s public key...')
client_pubKey = RSA.importKey(con.recv(4096), passphrase=None)

print('receiving client\'s AES key...')
aes_key = decrypter.decrypt(con.recv(4096))

file1 = open('./good', 'rb').read()
file2 = open('./evil', 'rb').read()

md5Hash1 = md5(file1).hexdigest()
md5Hash2 = md5(file2).hexdigest()
encrypter = PKCS1_OAEP.new(client_pubKey)
encrypted1 = encrypter.encrypt(bytes(md5Hash1,'utf-8'))
encrypted2 = encrypter.encrypt(bytes(md5Hash2,'utf-8'))

print('sending the first file to the client...')
con.send(encryptMsg('./good',aes_key)+encrypted1)
print('sending the second file to the client...')
con.send(encryptMsg('./evil',aes_key)+encrypted2)
print('files were sent successfully!')
sock.close()
