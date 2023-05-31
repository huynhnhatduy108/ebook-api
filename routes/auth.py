from fastapi import APIRouter, Depends, HTTPException
from functions.auth import generate_token, validate_token
from config.db import client
from schemas.user import serializeDict, serializeList, UserQueryParams, UserRegisterDto, UserLoginDto
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
    user = client.user.find_one({"_id":ObjectId(id)},{ "password":0})
    user = serializeDict(user)
    return JSONResponse(content=user, status_code=200)

@auth.post(
    path='/register',
    name="Register",
    description="User register",
)
async def register_user(user: UserRegisterDto):
    user_exist = client.user.find_one({"$or": [{"username":user.username, "email":user.email}]})
    if user_exist: 
        raise HTTPException(400, detail="User was existed!")
    user.password = gen_hash_password(user.password)
    client.user.insert_one(dict(user))
    
    return JSONResponse(content=user, status_code=201)


@auth.post(
    path='/login',
    name="Login",
    description="User login",
)
async def login_user(user: UserLoginDto):
    user_exist = client.user.find_one({"username":user.username})
    if not user_exist: 
        raise HTTPException(400, detail="Wrong user or password!")
    check_password = check_match_password(user.password,user_exist["password"])
    if check_password is False: 
        raise HTTPException(400, detail="Wrong user or password!")
    data ={
        "_id":str(user_exist["_id"]),
        "username":user_exist["username"],
        "email":user_exist["email"],
        "access_token":generate_token(str(user_exist["_id"]))
    }
    return JSONResponse(content=data, status_code=200)