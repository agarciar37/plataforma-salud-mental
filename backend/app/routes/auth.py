from fastapi import APIRouter, HTTPException, status
from app.db import db, users_collection
from app.schemas.auth import RegisterUserSchema, LoginUserSchema
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/ping")
def ping_auth():
    return {"message": "Ruta auth operativa"}


@router.get("/db-test")
def db_test():
    collections = db.list_collection_names()
    return {
        "message": "Conexión con MongoDB correcta",
        "collections": collections
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: RegisterUserSchema):
    existing_user = users_collection.find_one({"email": user.email})

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese email"
        )

    hashed_password = hash_password(user.password)

    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password
    }

    result = users_collection.insert_one(new_user)

    return {
        "message": "Usuario registrado correctamente",
        "user_id": str(result.inserted_id),
        "name": user.name,
        "email": user.email
    }


@router.post("/login")
def login(user: LoginUserSchema):
    existing_user = users_collection.find_one({"email": user.email})

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    if not verify_password(user.password, existing_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    token_data = {
        "sub": str(existing_user["_id"]),
        "email": existing_user["email"],
        "name": existing_user["name"]
    }

    access_token = create_access_token(token_data)

    return {
        "message": "Login correcto",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(existing_user["_id"]),
            "name": existing_user["name"],
            "email": existing_user["email"]
        }
    }