from hashing.sha256 import SHA256

sha256 = SHA256()
print(sha256.hash("Hello World"))
print(sha256.verify("Hello World", sha256.hash("Hello World")))
