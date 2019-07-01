from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_keys():
    """
    Generate private key and public key serialized bytes.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    return private_pem, public_pem


def main():
    "Write private.pem and public.pem in the current directory."
    private_pem, public_pem = generate_keys()
    with open('private.pem', 'wb') as file:
        file.write(private_pem)
    with open('public.pem', 'wb') as file:
        file.write(public_pem)


if __name__ == '__main__':
    main()
