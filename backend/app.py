from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from database import DatabaseConnection
from fastapi.responses import JSONResponse

# 加載環境變量
load_dotenv()

app = FastAPI(title="Stock Market API")

# CORS 设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 移除重复的路由注册
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

# 全局错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_message = str(exc)
    if "nodename nor servname provided" in error_message:
        return JSONResponse(
            status_code=503,
            content={"detail": "数据库连接失败，请检查数据库配置"}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": error_message}
    )

# 数据库连接管理
db = DatabaseConnection()

@app.on_event("startup")
async def startup():
    try:
        await db.connect()
    except Exception as e:
        print(f"数据库连接失败: {e}")

@app.on_event("shutdown")
async def shutdown():
    await db.close()

@app.get("/")
async def root():
    return {"message": "Stock Market API is running"}