from pwdlib import PasswordHash

PASSWORD_HASHER: PasswordHash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    return PASSWORD_HASHER.hash(plain_password)


def verify_password(plain_password: str, stored_password_hash: str) -> bool:
    return PASSWORD_HASHER.verify(password=plain_password, hash=stored_password_hash)
