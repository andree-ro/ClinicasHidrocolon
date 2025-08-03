import time
import sys
from itertools import cycle
import hashlib
import base64


class Metodo:

    def encrypt(self, n, plaintext, key):
        result = ''
        for x in plaintext.lower():
            try:
                i = (key.index(x) + n) % 26
                result += key[i]
            except ValueError:
                result += x
        return result.lower()

    def decrypt(self, n, ciphertext, key):
        result = ''
        for y in ciphertext.lower():
            try:
                i = (key.index(y) - n) % 26
                result += key[i]
            except ValueError:
                result += y
        return result.lower()

    def cadena(self, cadena):
        cadena_invertida = ""
        for letra in cadena:
            cadena_invertida = letra + cadena_invertida
        return cadena_invertida


class Metodos_refuerzo:

    def keygen(self, key):
        h = hashlib.sha256()
        h.update(key.encode())
        return base64.a85encode(h.digest()).decode()[:24]

    def rail_pattern(self, n):
        r = list(range(n))
        return cycle(r + r[-2:0:-1])

    def encode(self, plaintext, rails):
        p = self.rail_pattern(rails)
        return ''.join(sorted(plaintext, key=lambda i: next(p)))

    def decode(self, ciphertext, rails):
        p = self.rail_pattern(rails)
        indexes = sorted(range(len(ciphertext)), key=lambda i: next(p))
        result = [''] * len(ciphertext)
        for i, c in zip(indexes, ciphertext):
            result[i] = c
        return ''.join(result)

######

    def text2number(self, string__, x):
        if ord(string__[-1]) % 2 == 1:
            string__ = string__[::-1]
        return (int.from_bytes(string__.encode(), "little") % x) + 2

    def modEncrypt(self, msg, key):
        return "".join([chr((ord(msg[i]) + ord(key[i % len(key)])) % 256) for i in range(len(msg))])

    def modDecrypt(self, cip, key):
        return "".join([chr((ord(cip[i]) + (256 - ord(key[i % len(key)]))) % 256) for i in range(len(cip))])

######

    def xor(self, s, k):
        return "".join([chr(ord(f) ^ ord(k[i % len(k)])) for i, f in enumerate(s)])

######
    def split(self, seq):
        n = 12  # block length is 12
        datas = []
        while seq:
            datas.append(seq[:n])
            seq = seq[n:]
        return datas

    def pad(self, e):
        if len(e) == 12:
            return e
        else:
            return e + (chr(0) * (12 - len(e)))
        ######

    def encrypt(self, string, key):
        string = chr(len(string)) + string
        string = self.modEncrypt(string, key)
        ciphertext = ""
        odometer = [1, 2, 3, 4]
        blocks = self.split(string)
        key1 = key[12:24]
        key = key[:12]
        for block in blocks:
            block = self.pad(block)
            if odometer[0] == 1:
                for i in range(4):
                    block = self.modEncrypt(block, key1)
                    block = self.xor(block, key)
            elif odometer[1] == 1:
                for i in range(3):
                    block = self.xor(block, key)
                    block = self.modEncrypt(block, key)
            elif odometer[2] == 1:
                for i in range(2):
                    block = self.xor(block, key1)
                    block = self.modEncrypt(block, key1)
            elif odometer[3] == 1:
                block = self.modEncrypt(block, key1)
                block = self.xor(block, key1)
            odometer = odometer[1:] + [odometer[0]]
            ciphertext = ciphertext + block
        ciphertext = self.encode(ciphertext, self.text2number(key, 12))
        return self.xor(ciphertext, chr(self.text2number(key1, 127)) + chr(self.text2number(key, 127)))

    def decrypt(self, cipher, key):
        string = ""
        odometer = [1, 2, 3, 4]
        key1 = key[12:24]
        key = key[:12]
        cipher = self.xor(cipher, chr(self.text2number(key1, 127)) + chr(self.text2number(key, 127)))
        cipher = self.decode(cipher, self.text2number(key, 12))
        blocks = self.split(cipher)
        for block in blocks:
            if odometer[1] == 1:
                for i in range(3):
                    block = self.modDecrypt(block, key)
                    block = self.xor(block, key)
            elif odometer[0] == 1:
                for i in range(4):
                    block = self.xor(block, key)
                    block = self.modDecrypt(block, key1)
            elif odometer[3] == 1:
                block = self.xor(block, key1)
                block = self.modDecrypt(block, key1)
            elif odometer[2] == 1:
                for i in range(2):
                    block = self.modDecrypt(block, key1)
                    block = self.xor(block, key1)
            odometer = odometer[1:] + [odometer[0]]
            string = string + block
        final = list(self.modDecrypt(string, key + key1).rstrip())
        char = ord(final.pop(0))
        return "".join(final[:char])