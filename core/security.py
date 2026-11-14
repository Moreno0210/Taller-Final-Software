
import hashlib
import hmac
import os


ITERATIONS = 310_000


def get_password_hash(password: str) -> str:

    salt = os.urandom(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        ITERATIONS
    )

    return (
        f"pbkdf2_sha256${ITERATIONS}"
        f"${salt.hex()}${digest.hex()}"
    )


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    try:
        algorithm, iterations, salt_hex, digest_hex = (
            hashed_password.split("$")
        )

        if algorithm != "pbkdf2_sha256":
            return False

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations)
        )

        expected = bytes.fromhex(digest_hex)

        return hmac.compare_digest(actual, expected)

    except (ValueError, TypeError):
        return False
