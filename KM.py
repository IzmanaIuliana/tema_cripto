from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import socket
import random

k1 = get_random_bytes(AES.block_size)
k2 = get_random_bytes(AES.block_size)
k3 = b'abababababababab'
iv = b'dcdcdcdcdcdcdcdc'
vi = get_random_bytes(AES.block_size)

def padd_function(text):
    # cati biti adaugam
    dif = int(len(text) % AES.block_size)
    add = AES.block_size - dif
    padd_text = bytearray(text)
    padd_text.extend(bytearray([32] * add))
    return bytes(padd_text)

MODE = ""

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 5050))
server.listen(2)

print("asteptam nodurile A si B...")

clientA, addrA = server.accept()
print("Nod A conectat, asteptam modul ales...")
clientB, addrB = server.accept()
print("Nod B conectat, asteptam modul ales...")

data1 = clientA.recv(1024)
data2 = clientB.recv(1024)
print("A a ales: " + data1.decode("utf-8"))
print("B a ales: " + data2.decode("utf-8"))
print(
    "verificam daca modurile coincid, daca da acela va fi modul de criptare, daca nu, se va alege unul in mod random...")

if data1.decode("utf-8") == "ecb" and data2.decode("utf-8") == "ecb":
    MODE = "ecb"
else:
    if data1.decode("utf-8") == "cfb" and data2.decode("utf-8") == "cfb":
        MODE = "cfb"
    else:
        x = random.randint(0, 10)
        y = x % 2
        if y:
            MODE = "ecb"
        else:
            MODE = "cfb"

clientA.send(bytes(MODE, "utf-8"))
clientB.send(bytes(MODE, "utf-8"))

print("modul ales pentru criptare:  " + MODE)


if MODE == "ecb":
    print("urmeaza sa trimitem K1 catre nodurile A si B...")
    aes = AES.new(k3, AES.MODE_ECB)
    en_k1 = aes.encrypt(k1)
    clientA.send(en_k1)
    clientB.send(en_k1)
    print("am trimis cheia k1 catre A si B")

    print("asteptam confirmarea...")
    aes = AES.new(k1, AES.MODE_ECB)

    msg1 = clientA.recv(1024)
    msg2 = clientB.recv(1024)

    confA = aes.decrypt(msg1)
    confB = aes.decrypt(msg2)

    if confA == b"confirmAAAAAAAAA" and confB == b"confirmBBBBBBBBB":
        msg3 = "putem incepe comunicarea"
        clientA.send(bytes(msg3, "utf-8"))
        clientB.send(bytes(msg3, "utf-8"))
        print("confirmare primita, incepe comunicarea...")

else:
    if MODE == "cfb":
        print("urmeaza sa trimitem K2 si vectorul de initializare catre nodurile A si B...")
        aes = AES.new(k3, AES.MODE_CFB, iv)
        en_k2 = aes.encrypt(k2)
        en_vi = aes.encrypt(vi)

        clientA.send(en_k2)
        clientA.send(en_vi)

        clientB.send(en_k2)
        clientB.send(en_vi)
        print("am trimis cheia k2 si vectorul de initializare catre A si B")

        print("asteptam confirmarea...")

        aes = AES.new(k2, AES.MODE_CFB, vi)

        msg1 = clientA.recv(1024)
        msg2 = clientB.recv(1024)

        confA = aes.decrypt(msg1)
        aes = AES.new(k2, AES.MODE_CFB, vi)
        confB = aes.decrypt(msg2)

        if confA == b"confirmAAAAAAAAA" and confB == b"confirmBBBBBBBBB":
            msg3 = "putem incepe comunicarea"
            clientA.send(bytes(msg3, "utf-8"))
            clientB.send(bytes(msg3, "utf-8"))
            print("confirmare primita, incepe comunicarea...")

while True:
    if MODE =="ecb":
        aes = AES.new(k3,AES.MODE_ECB)

        m1=clientA.recv(1024)
        d_m1= aes.decrypt(m1)
        d_m1 = d_m1.decode("utf-8")
        d_m1 = d_m1.rstrip()
        if d_m1 == "gatagatagatagata":
            print("A a terminat")

        else:
            print("A: ",d_m1)

        aes = AES.new(k3, AES.MODE_ECB)
        m2=clientB.recv(1024)
        d_m2 = aes.decrypt(m2)
        d_m2 = d_m2.decode("utf-8")
        d_m2 = d_m2.rstrip()
        if d_m2 == "gatagatagatagata":
            print("B a terminat")

        else:
            print("B: ", d_m2)

        if d_m1 == "gatagatagatagata" and d_m2 == "gatagatagatagata":
            break

        if d_m1 == "am trimis 8 blocuri" and d_m2 =="am primit 8 blocuri":
            ras = padd_function(bytes("continua", "utf-8"))
            rasp = aes.encrypt(ras)
            clientA.send(rasp)
            clientB.send(rasp)


    if MODE =="cfb":
        aes = AES.new(k3,AES.MODE_CFB,iv)

        m1=clientA.recv(1024)
        d_m1= aes.decrypt(m1)
        d_m1 = d_m1.decode("utf-8")
        d_m1 = d_m1.rstrip()
        if d_m1 == "gatagatagatagata":
            print("A a terminat")

        else:
            print("A: ",d_m1)

        aes2 = AES.new(k3,AES.MODE_CFB,iv)

        m2=clientB.recv(1024)

        d_m2 = aes2.decrypt(m2)
        d_m2 = d_m2.decode("utf-8")
        d_m2 = d_m2.rstrip()
        if d_m2 == "gatagatagatagata":
            print("B a terminat")

        else:
            print("B: ", d_m2)

        if d_m1 == "gatagatagatagata" and d_m2 == "gatagatagatagata":
            break

        if d_m1 == "am trimis 8 blocuri" and d_m2 =="am primit 8 blocuri":
            ras = padd_function(bytes("continua", "utf-8"))
            aes = AES.new(k3, AES.MODE_CFB, iv)
            rasp = aes.encrypt(ras)
            clientA.send(rasp)
            clientB.send(rasp)




# cd C:\Users\Iulia\Desktop\SI\tema1
# python KM.py
# python A.py
# python B.py
# pip3 install pycryptodome (in directorul proiectului)
