
from fastapi import APIRouter, Depends, HTTPException
from config.constant import DASHBOARD
from functions.auth import generate_token, validate_token
from config.db import client
from bson import ObjectId
from fastapi.responses import JSONResponse
from models.common import NotificationModel
from schemas.common import NotiQueryParams

noti = APIRouter() 

@noti.get(  
    path='/',
    name="Noti To my site",
    description="Noti To my site",
)
async def list_noti(param:NotiQueryParams = Depends(), auth = Depends(validate_token)):

    match_condition = {"$and":[]}
    sort_condition = {}
    page = param.page
    page_size = param.page_size
    skip = page * page_size - page_size;

    if "keyword" in dict(param):
        if param.keyword:
            keyword_scope = {
                                "$or":[
                                        {"mess":{"$regex" : param.keyword, '$options': 'i'}},
                                      ]       
                            }
            
            match_condition["$and"].append(keyword_scope)
    
    if "ordering" in dict(param):
        sort_condition=param.ordering

    pipeline = [ 
              {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "post_id": { "$toString": "$post_id" },
                        "ebook_id": { "$toString": "$ebook_id" },
                    }
                },
             {
                    "$match": match_condition if match_condition["$and"] else {}
                },
              {
                    "$sort":sort_condition
                },
             {
                "$facet": {
                    "data": [{"$skip": skip},{"$limit": page_size}],
                    "count": [{"$count": "total_record"}]
                }
            },
        ]

    result = client.notification.aggregate(pipeline)
    result = list(result)
    items = result[0]["data"]
    total_record = 0
    if result[0]["data"]:
        total_record = result[0]["count"][0]["total_record"]

    data ={
        "items": items,
        "page":page,
        "page_size":page_size,
        "total_record":total_record
    }
    return data



@noti.get(  
    path='/noti/{noti_id}',
    name="Find nito by id",
    description="Find nito by id",
)
async def find_noti(noti_id,auth = Depends(validate_token)):
    noti = client.notification.find_one({"_id":ObjectId(noti_id)}, { "_id": { "$toString": "$_id" },
                        "post_id": { "$toString": "$post_id" },
                        "ebook_id": { "$toString": "$ebook_id" },"created_at":1, "updated_at":1, "mess":1})
    if not noti:
        raise HTTPException(404, detail="Noti not found!")
    
    return noti



@noti.post(  
    path='/',
    name="Noti To my site",
    description="Noti To my site",
)
async def creat_noti(model: NotificationModel):

    data = model.dict()
    client.notification.insert_one(data)

    return {"message":"Thank for your noti"}


@noti.delete(  
    path='/{noti_id}',
    name="Delete noti",
    description="Delete noti after fix",
)
async def delete_noti(noti_id, auth = Depends(validate_token)):

    client.notification.find_one_and_delete({"_id":ObjectId(noti_id)})

    return {"message":"Delete noti success"}



