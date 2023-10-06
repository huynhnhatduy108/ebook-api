from fastapi import APIRouter, Depends, HTTPException
from config.constant import DEFAULT_AVATAR_MAN, LOCAL_PROVIDER
from functions.auth import generate_token, validate_token
from config.db import client
from schemas.auth import FacabookLogin, GoogleLogin, UserRegisterDto, UserLoginDto
from bson import ObjectId
from functions.function import check_match_password, gen_hash_password
from fastapi.responses import JSONResponse

auth = APIRouter() 

@auth.get(
    path='/profile_user/{id}',
    name="Porfile User",
    description="Get profile user",
)
async def profile_user(id:str,auth: dict = Depends(validate_token)):
    user = client.user.find_one({"_id":ObjectId(id)},{ "password":0,"deleted_flag":0})
    user["_id"] = str(user["_id"])
    return JSONResponse(content=user, status_code=200)

@auth.post(
    path='/register',
    name="Register",
    description="User register",
)
async def register_user(user: UserRegisterDto):
    user_exist = client.user.find_one({
        "$or": [
            { "username": user.username } ,
            { "email":  user.email } 
        ]
    })

    if user_exist: 
        raise HTTPException(400, detail="Username or email was existed!")
    user.password = gen_hash_password(user.password)
    user = user.dict()
    client.user.insert_one(user)

    data ={
        "_id":str(user["_id"]),
        "username":user["username"],
        "email":user["email"],
    }
    
    return JSONResponse(content=data, status_code=201)


@auth.post(
    path='/login',
    name="Login",
    description="User login",
)
async def login_user(user: UserLoginDto):
    
    user_exist = client.user.find_one({
        "$or": [
            { "username": user.username } ,
            { "email":  user.username } 
        ]
    })
    if not user_exist: 
        raise HTTPException(400, detail="Wrong user or password!")
    
    check_password = check_match_password(user.password,user_exist["password"])
    if check_password is False: 
        raise HTTPException(400, detail="Wrong user or password!")
    
    data ={
        "_id":str(user_exist["_id"]),
        "username":user_exist["username"],
        "full_name":user_exist["full_name"],
        "avatar_url":user_exist.get("avatar_url", DEFAULT_AVATAR_MAN),
        "email":user_exist["email"],
        "provider": user_exist.get("provider", LOCAL_PROVIDER),
        "access_token":generate_token(str(user_exist["_id"]))
    }
    return JSONResponse(content=data, status_code=200)


@auth.post(
    path='/google_login',
    name="Google Login",
    description="Google login",
)
async def google_login(user: GoogleLogin):
    
    user_exist = client.user.find_one({
        "$or": [
            { "username": user.username } ,
            { "email":  user.username } 
        ]
    })
    if not user_exist: 
        user = user.dict()
        user_create = client.user.insert_one(user)
        data = {
            "_id":str(user_create.inserted_id),
            "username":user["username"],
            "email":user["email"],
            "avatar_url":user["avatar_url"],
            "provider": user["provider"],
            "access_token":generate_token(str(user_create.inserted_id))
        }

        return JSONResponse(content=user, status_code=200)

    data ={
        "_id":str(user_exist["_id"]),
        "username":user_exist["username"],
        "email":user_exist["email"],
        "avatar_url":user_exist.get("avatar_url", DEFAULT_AVATAR_MAN),
        "provider": user_exist.get("provider", LOCAL_PROVIDER),
        "access_token":generate_token(str(user_exist["_id"]))
    }
    return JSONResponse(content=data, status_code=200)


@auth.post(
    path='/facebook_login',
    name="Facebook Login",
    description="Facebook login",
)
async def facebook_login(user: FacabookLogin):
    
    user_exist = client.user.find_one({
        "$or": [
            { "username": user.username } ,
            { "email":  user.username } 
        ]
    })
    if not user_exist: 
        user = user.dict()
        user_create = client.user.insert_one(user)
        data = {
            "_id":str(user_create.inserted_id),
            "username":user["username"],
            "email":user["email"],
            "avatar_url":user["avatar_url"],
            "provider": user["provider"],
            "access_token":generate_token(str(user_create.inserted_id))
        }

        return JSONResponse(content=user, status_code=200)

    data ={
        "_id":str(user_exist["_id"]),
        "username":user_exist["username"],
        "email":user_exist["email"],
        "avatar_url":user_exist.get("avatar_url", DEFAULT_AVATAR_MAN),
        "provider": user_exist.get("provider", LOCAL_PROVIDER),
        "access_token":generate_token(str(user_exist["_id"]))
    }
    
    return JSONResponse(content=data, status_code=200)