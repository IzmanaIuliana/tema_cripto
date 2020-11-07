import socket
from Crypto.Cipher import AES

k3 = b'abababababababab'
iv = b'dcdcdcdcdcdcdcdc'
k1 = b""
k2 = b""
vi = b""


def xor_function(ba1, ba2):
    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])


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
aes = AES.new(k1, AES.MODE_ECB)
aesk = AES.new(k3, AES.MODE_ECB)
while True:

    if MODE == "ecb":

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

print(plaintext)
