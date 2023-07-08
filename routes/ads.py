from fastapi import APIRouter, Depends, HTTPException
from functions.auth import generate_token, validate_token
from functions.function import gen_slug_radom_string
from models.ads import Ads
from config.db import client
from schemas.ads import AdsQueryParams
from bson import ObjectId
from fastapi.responses import JSONResponse
from pymongo import ReturnDocument
import math

ads = APIRouter() 


@ads.get(
    path='/',
    name="List ads",
    description="Get list ads",
)
async def list_categories(param:AdsQueryParams = Depends()):
    match_condition = {"$and":[]}
    sort_condition ={}
    page = param.page
    page_size = param.page_size
    skip = page * page_size - page_size;

    if "keyword" in dict(param):
        if param.keyword:
            keyword_scope = {
                                "$or":[
                                        {"name":{"$regex" : param.keyword, '$options': 'i'}},
                                        {"sponsor":{"$regex" : param.keyword, '$options': 'i'}},
                                      ]       
                            }
            
            match_condition["$and"].append(keyword_scope)

    if "ordering" in dict(param):
        sort_condition=param.ordering

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
                        "deleted_flag": 0,
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
    

    result = client.ads.aggregate(pipline)
    result = list(result)

    items = result[0]["data"]
    total_record = 0
    if result[0]["data"]:
        total_record = result[0]["count"][0]["total_record"]
    
    data ={
        "items": items,
        "page":page,
        "page_size":page_size,
        "total_record":total_record,
        "total_page":math.ceil(total_record / page_size)
    }
    return data


@ads.get(
    path='/full',
    name="List ads full",
    description="Get list ads full",
)
async def list_ads_full():
 
    pipline=[
                 {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                    }
                },
                 {
                    "$project": {
                        "deleted_flag": 0,
                        "ebooks":0,
                        "posts":0,
                    }
                },
            ]
    

    result = client.ads.aggregate(pipline)
    result = list(result)
   
    return result


@ads.get(
    path='/{id}',
    name="Info ads by id",
    description="Info ads by id",
)
async def info_ads_by_id(id:str):
    ads = client.ads.find_one({"_id":ObjectId(id)},
                                         {  "_id": { "$toString": "$_id" },
                                            "name":1, 
                                            "width":1, 
                                            "height":1,
                                            "script":1,
                                            "sponsor":1,
                                            "created_at": 1,
                                            "updated_at":1
                                           })

    if not ads:
        raise HTTPException(404, detail="ads not found!")
    
    return ads

 
@ads.post(
    path='/',
    name="Create ads",
    description="Create ads",
)
async def create_ads(ads: Ads, auth: dict = Depends(validate_token)):

    ads = ads.dict()

    ads_create = client.ads.insert_one(ads)
    ads["_id"] = str(ads_create.inserted_id)

    return  ads


@ads.put(
    path='/{id}',
    name="update ads",
    description="update ads",
) 
async def update_ads(id, ads: Ads, auth: dict = Depends(validate_token)):

    ads_exist = client.ads.find_one({"_id":ObjectId(id)})
    if not ads_exist:
        raise HTTPException(404, detail="ads not found!")
    
    ads= ads.dict()

    ads_update = client.ads.find_one_and_update({"_id":ObjectId(id)},{
        "$set":ads
    }, return_document = ReturnDocument.AFTER)

    ads_update["_id"] = str(ads_update["_id"])

    return ads_update

@ads.delete(  
    path='/{id}',
    name="Delete ads",
    description="Delete ads",
)
async def delete_ads(id, auth: dict = Depends(validate_token)):

    # if auth["role"] !=1:
    #     raise HTTPException(403, detail="No permission!")

    ads = client.ads.find_one({"_id":ObjectId(id)})
    if not ads:
        raise HTTPException(404, detail="ads not found!")
    
    client.ads.find_one_and_delete({"_id":ObjectId(id)})
    return JSONResponse(content={"message":"Delete success"}, status_code=200)
