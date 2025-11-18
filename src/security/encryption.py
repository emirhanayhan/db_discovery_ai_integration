import json
from asyncio import wrap_future
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes



def generate_private_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    with open("encryption_private_key.pem", "wb") as f:
        f.write(pem_private)

async def decrypt_text(private_key, cipher, threadpool):
    ciphertext = bytes.fromhex(cipher)
    json_text = await wrap_future(
        threadpool.submit(
            private_key.decrypt, ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    )
    return json.loads(json_text.decode("utf-8"))
