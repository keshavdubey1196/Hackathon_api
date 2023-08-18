import secrets
import os


def generate_secret_key():
    """Returns a 32 char long secret key
       length is 32 by default
    """
    allowed_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(allowed_chars) for _ in range(50))


ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])


if __name__ == "__main__":
    # print(generate_secret_key())
    print(os.urandom(24))
