import bcrypt


class SecurityService:
    @staticmethod
    def hash_password(password: str) -> str:
        pw_bytes = password.encode('utf-8')

        salt = bcrypt.gensalt(rounds=12)

        hash = bcrypt.hashpw(pw_bytes, salt)

        return hash.decode('utf-8')

    @staticmethod
    def check_password(password: str, hashed_password) -> bool:
        pw_bytes = password.encode('utf-8')
        hash = hashed_password.encode('utf-8')

        return bcrypt.checkpw(pw_bytes, hash)
