import hashlib
def hash_password(password): #basic works
    return hashlib.sha256(password.encode()).hexdigest()