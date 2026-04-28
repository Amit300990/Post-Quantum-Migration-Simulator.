from app.core.classical.rsa import generate_rsa_keypair, serialize_private_key, serialize_public_key
from app.core.hybrid import RSAHybridCipher, KyberHybridCipher
from app.core.pqc.kyber import generate_kyber_keypair


def test_rsa_hybrid_encrypt_decrypt() -> None:
    private_key, public_key = generate_rsa_keypair()
    cipher = RSAHybridCipher(
        public_key=serialize_public_key(public_key),
        private_key=serialize_private_key(private_key),
    )
    message = b"secure migration simulator"
    payload = cipher.encrypt(message)
    plaintext = cipher.decrypt(payload)
    assert plaintext == message


def test_kyber_hybrid_encrypt_decrypt() -> None:
    keypair = generate_kyber_keypair()
    cipher = KyberHybridCipher(
        public_key=keypair["public_key"],
        private_key=keypair["private_key"],
    )
    message = b"post-quantum validation"
    payload = cipher.encrypt(message)
    plaintext = cipher.decrypt(payload)
    assert plaintext == message
