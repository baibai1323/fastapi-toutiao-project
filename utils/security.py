from passlib.context import CryptContext

# 使用 pbkdf2_sha256，无需安装额外库，无长度限制
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], default="pbkdf2_sha256")

def get_hash_password(password: str) -> str:
    """对密码进行哈希加密"""
    return pwd_context.hash(password)

def get_verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否正确"""
    return pwd_context.verify(plain_password, hashed_password)
