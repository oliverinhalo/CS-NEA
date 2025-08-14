def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()