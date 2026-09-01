from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from src.core.config import settings

# Em produção, a secret key vem do vault/ambiente
SECRET_KEY = settings.SECRET_KEY
serializer = URLSafeTimedSerializer(SECRET_KEY)

def generate_signed_token(shipment_id: int, tenant_id: int) -> str:
    """Cria um payload assinado e protegido contra adulterações (HMAC)"""
    return serializer.dumps({
        "shipment_id": shipment_id,
        "tenant_id": tenant_id
    })

def verify_signed_token(token: str, max_age: int = 86400) -> dict:
    """
    Desempacota o token.
    Lança ValueError se a assinatura não bater ou o tempo estourar.
    """
    try:
        return serializer.loads(token, max_age=max_age)
    except SignatureExpired:
        raise ValueError("Token expired")
    except BadSignature:
        raise ValueError("Invalid token signature")

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def generate_tenant_token(tenant_id: int, role: str) -> str:
    return serializer.dumps({
        "tenant_id": tenant_id,
        "role": role
    })

def verify_tenant_token(token: str, max_age: int = 86400 * 7) -> dict:
    try:
        payload = serializer.loads(token, max_age=max_age)
        if "role" not in payload:
            raise ValueError("Invalid tenant token payload")
        return payload
    except SignatureExpired:
        raise ValueError("Token expired")
    except BadSignature:
        raise ValueError("Invalid token signature")
