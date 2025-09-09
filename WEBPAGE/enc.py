def hash_password(password): #basic works
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()