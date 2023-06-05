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
async def list_users(param:UserQueryParams = Depends(), auth: dict = Depends(validate_token)):
    match_condition = {"$and":[]}
    page = param.page
    page_size = param.page_size
    skip = page * page_size - page_size;

    if "keyword" in dict(param):
        if param.keyword:
            keyword_scope = {
                                "$or":[
                                        {"username":{"$regex" : param.keyword, '$options': 'i'}},
                                        {"email":{"$regex" : param.keyword, '$options': 'i'}},
                                      ]       
                            }
            
            match_condition["$and"].append(keyword_scope)

    if "role" in dict(param):
        if param.role:
            cates_scope = {"role":param.role }
            match_condition["$and"].append(cates_scope)

    if "provider" in dict(param):
        if param.provider:
            cates_scope = {"provider":param.provider}
            match_condition["$and"].append(cates_scope)

    pipline=[
                {
                    "$match": match_condition if match_condition["$and"] else {}
                },
                {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        }
                },
                {
                    "$project": {
                        "deleted_flag": 0 ,
                        "password":0,
                    }
                },
                {
                    "$facet": {
                        "data": [{"$skip": skip},{"$limit": page_size}],
                        "count": [{"$count": "total_record"}]
                    }
                },
            ]

    result = client.user.aggregate(pipline)
    result = list(result)

    items = result[0]["data"]

    # print("items==>", items)
    total_record = 0
    if result[0]["data"]:
        total_record = result[0]["count"][0]["total_record"]

    data ={
        "items": items,
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
