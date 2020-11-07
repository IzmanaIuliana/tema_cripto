import socket
from Crypto.Cipher import AES
import time

k3 = b'abababababababab'
iv = b'dcdcdcdcdcdcdcdc'
k1 = b""
k2 = b""
vi = b""


def xor_function(s1, s2):
    return bytes([i ^ j for i, j in zip(s1, s2)])




def padd_function(text):
    # cati biti adaugam
    dif = int(len(text) % AES.block_size)
    add = AES.block_size - dif
    padd_text = bytearray(text)
    padd_text.extend(bytearray([32] * add))
    return bytes(padd_text)


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5050))
mode = ""
MODE = ""

while True:
    inp = input("trimiteti modul de criptare,ecb sau cfb: ")
    if inp == "ecb":
        mode = "ecb"
        break
    else:
        if inp == "cfb":
            mode = "cfb"
            break
        else:
            print("mod invalid! tastati ecb sau cfb!")

client.send(bytes(mode, "utf-8"))
print("modul meu ales este: " + mode)
msg = client.recv(1024)

if msg.decode("utf-8") == "ecb":
    MODE = "ecb"
else:
    if msg.decode("utf-8") == "cfb":
        MODE = "cfb"

print("modul ales de KM este: " + MODE)

if MODE == "ecb":
    key = client.recv(1024)
    aes = AES.new(k3, AES.MODE_ECB)
    k1 = aes.decrypt(key)

    aes = AES.new(k1, AES.MODE_ECB)
    en_conf = aes.encrypt(bytes("confirmAAAAAAAAA", "utf-8"))

    client.send(en_conf)

else:
    if MODE == "cfb":
        key = client.recv(1024)
        v = client.recv(1024)

        aes = AES.new(k3, AES.MODE_CFB, iv)
        k2 = aes.decrypt(key)
        vi = aes.decrypt(v)

        aes = AES.new(k2, AES.MODE_CFB, vi)
        en_conf = aes.encrypt(bytes("confirmAAAAAAAAA", "utf-8"))
        client.send(en_conf)

msg = client.recv(1024).decode("utf-8")
print(msg)

fisier = open("plaintext.txt", "r")
plaintext = bytes(fisier.read().encode())

plaintext = padd_function(plaintext)

nr_blocuri = len(plaintext) // AES.block_size
stop = len(plaintext) - 1

socketB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketB.bind(('127.0.0.1', 5051))
socketB.listen(1)

socketB, addrB = socketB.accept()

if MODE == "ecb":
    aes = AES.new(k1, AES.MODE_ECB)
    aesK = AES.new(k3, AES.MODE_ECB)
    bl = 0
    for i in range(0, stop, 16):
        j = i + 16
        bloc = plaintext[i:j]
        en_bloc = aes.encrypt(bloc)

        if bl % 8 == 0 and bl > 0:
            msg = padd_function(bytes("am trimis 8 blocuri", "utf-8"))
            en_msg = aesK.encrypt(msg)
            client.send(en_msg)
            ras = client.recv(1024)
            cont = aesK.decrypt(ras)
            cont = cont.decode("utf-8")
            print("Km spune: ", cont)
        socketB.send(en_bloc)
        bl = bl + 1

        print("am trimis:", bl, " blocuri")

    gata = b"gatagatagatagata"
    aes = AES.new(k1, AES.MODE_ECB)
    end = aes.encrypt(gata)
    socketB.send(end)
    aesk = AES.new(k3, AES.MODE_ECB)
    end = aesk.encrypt(gata)
    client.send(end)

if MODE == "cfb":

    aes1 = AES.new(k2,AES.MODE_CFB,vi)
    n = str(nr_blocuri)
    n = padd_function(bytes(n, "utf-8"))
    en_n = aes1.encrypt(n)
    socketB.send(en_n)

    VI = vi

    bl = 0
    for i in range(0, stop, 16):
        j = i + 16
        bloc = plaintext[i:j]

        aes_k = AES.new(k2, AES.MODE_CFB, vi)
        vec = aes_k.encrypt(VI)
        res = xor_function(vec, bloc)

        VI = res

        if bl % 8 == 0 and bl > 0:
            msg = padd_function(bytes("am trimis 8 blocuri", "utf-8"))
            aeskk = AES.new(k3,AES.MODE_CFB,iv)
            en_msg = aeskk.encrypt(msg)
            client.send(en_msg)

            ras = client.recv(1024)

            aeskk = AES.new(k3, AES.MODE_CFB, iv)
            cont = aeskk.decrypt(ras)
            cont = cont.decode("utf-8")
            print("Km spune: ", cont)


        time.sleep(2)
        socketB.send(res)
        bl = bl + 1

        print("am trimis:", bl, " blocuri")

    gata = b"gatagatagatagata"

    aes = AES.new(k2, AES.MODE_CFB,vi)
    end = aes.encrypt(gata)
    socketB.send(end)

    aesk = AES.new(k3, AES.MODE_CFB,iv)
    end = aesk.encrypt(gata)
    client.send(end)
