from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from routes.user import user as user_router
from routes.auth import auth as auth_router
from routes.ebook import ebook as ebook_router
from routes.category import category as category_router
from routes.post import post as post_router
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
app.include_router(category_router, tags=["C. Category"], prefix="/category")
app.include_router(ebook_router, tags=["D. Ebook"], prefix="/ebook")
app.include_router(post_router, tags=["E. Post"], prefix="/post")
