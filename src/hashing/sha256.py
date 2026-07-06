from hashing.hasher import Hasher
import os


class SHA256(Hasher):
    def hash_with_salt(self, data: str, salt: bytes = None) -> str:
        if salt is None:
            salt = os.urandom(16)

        data_bytes = data.encode("utf-8")

        hashed = self._sha256(salt + data_bytes)

        return hashed, salt

    def verify_with_salt(self, data: str, hash: str, salt: bytes = None) -> bool:
        if salt is None:
            return self._sha256(data.encode("utf-8")) == hash
        return self._sha256(salt + data.encode("utf-8")) == hash

    def hash_raw(self, data: str) -> str:
        data_bytes = data.encode("utf-8")
        return self._sha256(data_bytes)

    def verify_raw(self, data: str, hash: str) -> bool:
        return self._sha256(data.encode("utf-8")) == hash

    @staticmethod
    def _sha256(message: bytes):
        def sqrt(n):
            return n**0.5

        def cbrt(n):
            return n ** (1 / 3)

        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(sqrt(n)) + 1):
                if n % i == 0:
                    return False
            return True

        def get_first_primes(n):
            primes = [2, 3]
            if n == 0:
                return []
            if n == 1:
                return [2]
            i = 3
            while len(primes) < n:
                i += 2
                if is_prime(i):
                    primes.append(i)

            return primes

        primes = get_first_primes(64)
        h_primes = []
        k_primes = []

        for i in range(8):
            h_primes.append(int((sqrt(primes[i]) - int(sqrt(primes[i]))) * (2**32)))

        for i in range(64):
            k_primes.append(int((cbrt(primes[i]) - int(cbrt(primes[i]))) * (2**32)))

        message_bytes = "".join([bin(i)[2:].zfill(8) for i in message])

        L = len(message_bytes)

        message_bytes += "1"

        final_length = 512 * ((len(message_bytes) + 512 + 64) // 512)

        message_bytes += "0" * (final_length - len(message_bytes) - 64)

        message_bytes += bin(L)[2:].zfill(64)

        right_rotate = lambda x, n: ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

        for i in range(0, len(message_bytes), 512):
            chunk = message_bytes[i : i + 512]
            w = []
            for j in range(0, 512, 32):
                w.append(chunk[j : j + 32])

            w.extend([""] * (64 - len(w)))

            for j in range(16, 64):
                j15 = int(w[j - 15], 2)
                j2 = int(w[j - 2], 2)
                s0 = right_rotate(j15, 7) ^ right_rotate(j15, 18) ^ (j15 >> 3)
                s1 = right_rotate(j2, 17) ^ right_rotate(j2, 19) ^ (j2 >> 10)
                w[j] = bin(
                    (int(w[j - 16], 2) + s0 + int(w[j - 7], 2) + s1) & 0xFFFFFFFF
                )[2:].zfill(32)

            a, b, c, d, e, f, g, h = h_primes

            for j in range(64):
                S1 = right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25)
                ch = (e & f) ^ (((~e) & 0xFFFFFFFF) & g)
                temp1 = (h + S1 + ch + k_primes[j] + int(w[j], 2)) & 0xFFFFFFFF
                S0 = right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22)
                maj = (a & b) ^ (a & c) ^ (b & c)
                temp2 = (S0 + maj) & 0xFFFFFFFF

                h = g
                g = f
                f = e
                e = (d + temp1) & 0xFFFFFFFF
                d = c
                c = b
                b = a
                a = (temp1 + temp2) & 0xFFFFFFFF

            working = [a, b, c, d, e, f, g, h]
            h_primes = [(h_primes[k] + working[k]) & 0xFFFFFFFF for k in range(8)]

        result = "".join([hex(i)[2:].zfill(8) for i in h_primes])

        return result
