
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
                    "$lookup": {
                        "from": "ebook",
                        "localField": "ebook_id",
                        "foreignField": "_id",
                        "as": "ebook_docs"
                    }
                },
                 {
                    "$lookup": {
                        "from": "post",
                        "localField": "post_id",
                        "foreignField": "_id",
                        "as": "post_docs"
                    }
                },
                {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "ebook":{
                            "_id": { "$toString": { "$arrayElemAt": [ "$ebook_docs._id", 0 ] } },
                            "_name": { "$arrayElemAt": [ "$ebook_docs.name", 0 ] },
                        },
                        "post":{
                            "_id": { "$toString": { "$arrayElemAt": [ "$post_docs._id", 0 ] } },
                            "_name": { "$arrayElemAt": [ "$post_docs.name", 0 ] },
                        },
                    }
                },
                {
                    "$match": match_condition if match_condition["$and"] else {}
                },
                {
                    "$project": {
                        "ebook_docs":0,
                        "post_docs":0,
                        "ebook_id":0, 
                        "post_id":0, 

                    }
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
    
    pipeline = [ 
                {
                    "$match": {"_id":ObjectId(noti_id)}
                },
                {
                    "$lookup": {
                        "from": "ebook",
                        "localField": "ebook_id",
                        "foreignField": "_id",
                        "as": "ebook_docs"
                    }
                },
                 {
                    "$lookup": {
                        "from": "post",
                        "localField": "post_id",
                        "foreignField": "_id",
                        "as": "post_docs"
                    }
                },
                {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "ebook":{
                            "_id": { "$toString": { "$arrayElemAt": [ "$ebook_docs._id", 0 ] } },
                            "_name": { "$arrayElemAt": [ "$ebook_docs.name", 0 ] },
                        },
                        "post":{
                            "_id": { "$toString": { "$arrayElemAt": [ "$post_docs._id", 0 ] } },
                            "_name": { "$arrayElemAt": [ "$post_docs.name", 0 ] },
                        },
                    }
                },
                {
                    "$project": {
                        "ebook_docs":0,
                        "post_docs":0,
                        "ebook_id":0, 
                        "post_id":0, 

                    }
                },
        ]
    notis = client.notification.aggregate(pipeline)
    
    noti = next(notis, None)

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



