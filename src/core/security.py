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
