from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

router = APIRouter()
security = HTTPBasic()

# Configuración básica de autenticación (deberías cambiar esto)
USERNAME = "admin"
PASSWORD = "fancontrol"

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@router.get("/secure-test")
async def secure_endpoint(username: str = Depends(verify_credentials)):
    return {"message": f"Hello {username}", "status": "authenticated"}