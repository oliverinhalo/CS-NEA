import hashlib

def cusotom(password):
    hashed = 0
    for index, char in enumerate(password):
        hashed += ord(char) * 31 * index

    return str(hashed)

def hash_password(password):
    password = cusotom(password)
    return hashlib.sha256(password.encode()).hexdigest()