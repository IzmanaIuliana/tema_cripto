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
    en_conf = aes.encrypt(bytes("confirmBBBBBBBBB", "utf-8"))
    client.send(en_conf)

else:
    if MODE == "cfb":
        key = client.recv(1024)
        v = client.recv(1024)

        aes = AES.new(k3, AES.MODE_CFB, iv)
        k2 = aes.decrypt(key)
        vi = aes.decrypt(v)

        aes = AES.new(k2, AES.MODE_CFB, vi)
        en_conf = aes.encrypt(bytes("confirmBBBBBBBBB", "utf-8"))
        client.send(en_conf)

msg = client.recv(1024).decode("utf-8")
print(msg)

socketA = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketA.connect(('127.0.0.1', 5051))
bl = 0
plaintext=""


VI = vi
if MODE == "ecb":

    while True:

        if bl % 8 == 0 and bl > 0:
            msg = padd_function(bytes("am primit 8 blocuri", "utf-8"))
            aesk = AES.new(k3, AES.MODE_ECB)
            en_msg = aesk.encrypt(msg)
            client.send(en_msg)
            ras = client.recv(1024)
            aesk = AES.new(k3, AES.MODE_ECB)
            cont = aesk.decrypt(ras)
            cont = cont.decode("utf-8")
            print("Km spune: ", cont)

        bloc = socketA.recv(1024)

        block = aes.decrypt(bloc)

        if block.decode("utf-8") == "gatagatagatagata":
            aeskk = AES.new(k3, AES.MODE_ECB)
            end = aeskk.encrypt(block)
            client.send(end)
            break
        else:
            plaintext = plaintext + block.decode("utf-8")
        bl = bl + 1
        print("am primit: ", bl, " blocuri")

if MODE == "cfb":
    aess = AES.new(k2, AES.MODE_CFB, vi)
    n = socketA.recv(1024)
    nr = aess.decrypt(n)
    nrr = str(nr.decode("utf-8"))
    ress = [int(i) for i in nrr.split() if i.isdigit()]
    NR = ress[0]
    print(NR)
    while True:


        aes_k = AES.new(k2, AES.MODE_CFB, vi)
        vec = aes_k.encrypt(VI)

        if bl % 8 == 0 and bl > 0:
            msg = padd_function(bytes("am primit 8 blocuri", "utf-8"))
            aes1 = AES.new(k3, AES.MODE_CFB,iv)
            en_msg = aes1.encrypt(msg)
            client.send(en_msg)

            ras = client.recv(1024)

            aes11 = AES.new(k3, AES.MODE_CFB,iv)
            cont = aes11.decrypt(ras)
            cont = cont.decode("utf-8")
            print("Km spune: ", cont)

        time.sleep(1)
        bloc = socketA.recv(1024)
        if (bl < NR):
            VI = bloc
        bl = bl + 1


        block = xor_function(bloc,vec)
        blc = block.decode("utf-8")
        print(blc)

        if blc == "gatagatagatagata":
            print(plaintext)
            client.send(block)
            break
        else:
            plaintext = plaintext + blc
            print("am primit: ", bl, " blocuri")

print(plaintext)
