from hashing.sha256 import SHA256

sha256 = SHA256()
hash, salt = sha256.hash_with_salt("Hello World")
print(hash, salt)
print(sha256.verify_with_salt("Hello World", hash, salt))
