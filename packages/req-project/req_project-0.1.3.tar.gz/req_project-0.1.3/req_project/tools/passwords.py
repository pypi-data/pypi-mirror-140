from passlib.hash import pbkdf2_sha256 

class Passwords:
    # init method or constructor   
    def __init__(self):
        self = self

    def encrypt_password(password):
        return pbkdf2_sha256.encrypt(password)


    def check_encrypted_password(password, hashed):
        return pbkdf2_sha256.verify(password, hashed)
