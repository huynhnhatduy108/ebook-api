from fastapi import APIRouter, Depends, HTTPException
from functions.auth import generate_token, validate_token
from models.user import User
from config.db import client
from schemas.user import serializeDict, serializeList, UserQueryParams
from bson import ObjectId
from fastapi.responses import JSONResponse

user = APIRouter() 

@user.get(
    path='/',
    name="List users",
    description="Get list info user",
)
async def list_users(auth: dict = Depends(validate_token), model:UserQueryParams = Depends()):
    query = {}
    page = model.page
    page_size = model.page_size
    skip = page * page_size - page_size;
    if "keyword" in dict(model):
        if model.keyword:
            query["$or"] = [{"username":{"$regex" : model.keyword, '$options': 'i'}},{"email":{"$regex" : model.keyword, '$options': 'i'}}]
    if "role" in dict(model):
        if model.role:
            query["role"] = 0

    users = client.user.find(query,{"password":0})
    users = users.skip(skip).limit(page_size)
    total_record = client.user.count_documents(query)

    users = serializeList(users)
    data ={
        "items": users,
        "page":page,
        "page_size":page_size,
        "total_record":total_record
    }
    return JSONResponse(content=data, status_code=200)


@user.put(
    path='/{id}',
    name="Update user",
    description="Update info user",
)
async def update_user(id, user: User, auth: dict = Depends(validate_token)):
    client.local.user.find_one_and_update({"_id":ObjectId(id)},{
        "$set":dict(user)
    })
    return serializeDict(client.user.find_one({"_id":ObjectId(id)}))

@user.delete(  
    path='/{id}',
    name="Delete user",
    description="Delete user",
)
async def delete_user(id, auth: dict = Depends(validate_token)):
    user = client.user.find_one({"_id":ObjectId(auth)},{ "password":0})
    if user["role"] !=1:
        raise HTTPException(403, detail="No permission!")
    client.user.find_one_and_delete({"_id":ObjectId(id)})
    return JSONResponse(content={"message":"Delete success"}, status_code=200)
