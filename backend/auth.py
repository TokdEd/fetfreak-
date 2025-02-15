import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from database import DatabaseConnection
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from models import User
from database import Database

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

class Auth:
    def __init__(self):
        self.db = DatabaseConnection()
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key')  # 環境變量中的密鑰

    def hash_password(self, password: str) -> str:
        """
        使用 bcrypt 加密密碼
        """
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        驗證密碼是否匹配
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def generate_token(self, user_id: int) -> str:
        """
        根據用戶 ID 生成 JWT
        """
        expiration = datetime.utcnow() + timedelta(hours=1)  # 設定 1 小時過期
        payload = {
            'user_id': user_id,
            'exp': expiration
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token

    def verify_token(self, token: str) -> dict:
        """
        驗證 JWT 並返回負載
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    async def register(self, name: str, email: str, password: str):
        """
        註冊新用戶
        """
        # 密碼加密
        hashed_password = self.hash_password(password)
        
        # 創建用戶
        user = await self.db.get_client().create_user(name, email, hashed_password)
        if user:
            return {"message": "User created successfully", "user_id": user.id}
        else:
            return {"message": "Error creating user"}

    async def login(self, email: str, password: str):
        """
        用戶登入，驗證密碼並生成 JWT
        """
        user = await self.db.get_client().get_user_by_email(email)
        if not user:
            return {"message": "User not found"}
        
        if not self.verify_password(password, user.password):
            return {"message": "Incorrect password"}
        
        # 生成 token
        token = self.generate_token(user.id)
        return {"message": "Login successful", "token": token}

    async def get_current_user(self, token: str):
        """
        解析 JWT，返回當前用戶信息
        """
        payload = self.verify_token(token)
        user = await self.db.get_client().get_user_by_id(payload['user_id'])
        return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Auth.secret_key, algorithms=["HS256"])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
        
    user = await DatabaseConnection().get_client().get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    # 检查邮箱是否已存在
    db = Database()
    existing_user = await db.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建新用户
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    new_user = await db.create_user(
        name=user.name,
        email=user.email,
        password=hashed_password.decode()
    )
    
    return UserResponse(
        id=new_user.id,
        name=new_user.name,
        email=new_user.email
    )

@router.post("/login")
async def login(login_data: LoginRequest):
    try:
        db = DatabaseConnection().get_client()
        user = await db.get_user_by_email(login_data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
            
        auth = Auth()
        if not auth.verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        token = auth.generate_token(user.id)
        return {"token": token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email
    )

# 使用範例
"""
async def main():
    auth = Auth()

    # 註冊新用戶
    register_response = await auth.register("John Doe", "john@example.com", "password123")
    print(register_response)
    
    # 用戶登入
    login_response = await auth.login("john@example.com", "password123")
    print(login_response)
    
    if "token" in login_response:
        # 使用 JWT 獲取當前用戶
        current_user = await auth.get_current_user(login_response["token"])
        print(current_user)

import asyncio
asyncio.run(main())
"""