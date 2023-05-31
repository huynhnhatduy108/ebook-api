from fastapi import FastAPI
from routes.user import user as user_router
from routes.auth import auth as auth_router
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EBOOK",
    debug=True,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    # allow_headers=["POST", "GET"],
)

app.include_router(auth_router, tags=["A. Auth"], prefix="/auth")
app.include_router(user_router, tags=["B. Users"], prefix="/user")
