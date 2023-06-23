from fastapi import APIRouter, Depends, HTTPException
from config.constant import BOOK_THUMBNAIL_PATH, CLOUDINARY_CLOUD_URL, DASHBOARD, FIREBASE_CLOUD_URL
from crawl.crawl import crawl_data
from crawl.lazada import lazada_crawl
from functions.auth import generate_token, validate_token
from functions.function import compare_old_to_new_list, gen_slug_radom_string
from models.ebook import Ebook, EbookRate
from config.db import client
from schemas.ebook import EbookQueryParams, serializeDict, serializeList
from bson import ObjectId
from fastapi.responses import JSONResponse
from pymongo import ReturnDocument, UpdateOne
import math

ebook = APIRouter() 

def get_ebook_by_id_or_slug(match={}):
    ebooks = client.ebook.aggregate([
                {
                    "$lookup": {
                        "from": "category",
                        "localField": "categories",
                        "foreignField": "_id",
                        "as": "categories"
                    }
                },
                {
                    "$lookup": {
                        "from": "user",
                        "localField": "created_by",
                        "foreignField": "_id",
                        "as": "created_by"
                    }
                },
                {
                    "$lookup": {
                        "from": "ebook_rate",
                        "localField": "_id",
                        "foreignField": "ebook_id",
                        "as": "ebook_rate"
                    }
                },
                 {
                    "$match": match
                },
                {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "categories": {
                            "$map": {
                                "input": "$categories",
                                "as": "category",
                                "in": {
                                    "_id": { "$toString": "$$category._id" },
                                    "name": "$$category.name",
                                    "name_en": "$$category.name_en",
                                    "description": "$$category.description"
                                }
                            }
                        },
                        "admin":{
                            "username": { "$arrayElemAt": ["$created_by.username", 0] },
                            "full_name": { "$arrayElemAt": ["$created_by.full_name", 0] },
                        },
                        "rate.size": { "$size": "$ebook_rate" },
                        "rate.average_rate": "$average_rate" ,
                        "img_url": {
                            "$cond": {
                                "if": { "$eq": [ "$img_url", "" ] },
                                "then": "",
                                "else": {
                                "$concat": [
                                    FIREBASE_CLOUD_URL,
                                    BOOK_THUMBNAIL_PATH,
                                    { "$ifNull": [ "$img_url", "" ] },
                                    "?alt=media"
                                ]
                                }
                            }
                        }

                    }
                },
                {
                    "$project": {
                        "deleted_flag": 0,
                        "created_by":0,
                        "updated_by":0,
                        "ebook_rate":0,
                        "average_rate":0
                    }
                }
            ])
    
    ebook = next(ebooks, None)

    if not ebook:
        raise HTTPException(404, detail="Ebook not found!")
    
    comments = client.ebook_comment.aggregate([
                {
                    "$lookup": {
                        "from": "user",
                        "localField": "user_id",
                        "foreignField": "_id",
                        "as": "user"
                    }
                },
                 {
                    "$match": match
                },
                {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "user_comment":{
                            "username": { "$arrayElemAt": ["$user.username", 0] },
                            "full_name": { "$arrayElemAt": ["$user.full_name", 0] },
                        }
                    }
                },
                {
                    "$project": {
                        "deleted_flag": 0,
                        "ebook_id":0,
                        "user_id":0,
                        "user":0,
                    }
                }
            ])
    ebook["comments"]= list(comments)

    return ebook

@ebook.get(
    path='/',
    name="List ebook",
    description="Get list ebook",
)
async def list_ebooks(param:EbookQueryParams = Depends()):
    match_condition = {"$and":[{"is_public":True}]}
    page = param.page
    page_size = param.page_size
    skip = page * page_size - page_size;
    sort_condition = {}

    if "keyword" in dict(param):
        if param.keyword:
            keyword_scope = {
                                "$or":[
                                        {"name":{"$regex" : param.keyword, '$options': 'i'}},
                                        {"content":{"$regex" : param.keyword, '$options': 'i'}},
                                        {"intro":{"$regex" : param.keyword, '$options': 'i'}},
                                        {"slug":{"$regex" : gen_slug_radom_string(param.keyword,0), '$options': 'i'}},
                                      ]       
                            }
            
            match_condition["$and"].append(keyword_scope)

    if "categories" in dict(param):
        if param.categories:
            cates_scope = {"categories._id":{"$in":param.categories} }
            match_condition["$and"].append(cates_scope)

    if "tags" in dict(param):
        if param.tags:
            tags_scope = {"tags":{"$in":param.tags} }
            match_condition["$and"].append(tags_scope)

    if "language" in dict(param):
        if param.language:
            language_scopes={"language":param.language }
            match_condition["$and"].append(language_scopes)

    if "ordering" in dict(param):
        sort_condition=param.ordering
    

    pipline=[
                {
                    "$match": match_condition if match_condition["$and"] else {}
                },
                {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "img_url": {
                            "$cond": {
                                "if": { "$eq": [ "$img_url", "" ] },
                                "then": "",
                                "else": {
                                "$concat": [
                                    FIREBASE_CLOUD_URL,
                                    BOOK_THUMBNAIL_PATH,
                                    { "$ifNull": [ "$img_url", "" ] },
                                    "?alt=media"
                                ]
                                }
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "_id":1, 
                        "name":1,
                        "img_url":1,
                        "average_rate":1,
                        "views":1,
                        "downloads":1,
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

    result = client.ebook.aggregate(pipline)
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

@ebook.get(
    path='/admin',
    name="List ebook admin",
    description="Get list ebook admin",
)
async def list_ebooks_admin(param:EbookQueryParams = Depends(),auth: dict = Depends(validate_token)):
    match_condition = {"$and":[]}
    page = param.page
    page_size = param.page_size
    skip = page * page_size - page_size;
    sort_condition = {}

    if "keyword" in dict(param):
        if param.keyword:
            keyword_scope = {
                                "$or":[
                                        {"name":{"$regex" : param.keyword, '$options': 'i'}},
                                        {"content":{"$regex" : param.keyword, '$options': 'i'}},
                                        {"intro":{"$regex" : param.keyword, '$options': 'i'}},
                                        {"slug":{"$regex" : gen_slug_radom_string(param.keyword,0), '$options': 'i'}},
                                      ]       
                            }
            
            match_condition["$and"].append(keyword_scope)

    if "categories" in dict(param):
        if param.categories:
            cates_scope = {"categories._id":{"$in":param.categories} }
            match_condition["$and"].append(cates_scope)

    if "tags" in dict(param):
        if param.tags:
            tags_scope = {"tags":{"$in":param.tags} }
            match_condition["$and"].append(tags_scope)

    if "language" in dict(param):
        if param.language:
            language_scopes={"language":param.language }
            match_condition["$and"].append(language_scopes)

    if "ordering" in dict(param):
        sort_condition=param.ordering
    

    pipline=[
                {
                    "$lookup": {
                        "from": "category",
                        "localField": "categories",
                        "foreignField": "_id",
                        "as": "categories"
                    }
                },
                {
                    "$match": match_condition if match_condition["$and"] else {}
                },
                {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "categories": {
                            "$map": {
                                "input": "$categories",
                                "as": "category",
                                "in": {
                                    "_id": { "$toString": "$$category._id" },
                                    "name": "$$category.name",
                                    "name_en": "$$category.name_en",
                                    "description": "$$category.description"
                                }
                            }
                        },
                        "img_url": {
                            "$cond": {
                                "if": { "$eq": [ "$img_url", "" ] },
                                "then": "",
                                "else": {
                                "$concat": [
                                    FIREBASE_CLOUD_URL,
                                    BOOK_THUMBNAIL_PATH,
                                    { "$ifNull": [ "$img_url", "" ] },
                                    "?alt=media"
                                ]
                                }
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "_id":1, 
                        "name":1,
                        "img_url":1,
                        "tags":1,
                        "average_rate":1,
                        "views":1,
                        "language":1,
                        "downloads":1,
                        "categories":1
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

    result = client.ebook.aggregate(pipline)
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


@ebook.get(
    path='/{id}',
    name="Info ebook by id",
    description="Info ebook by id",
)
async def info_ebook_by_id(id:str):

    match = {"_id":ObjectId(id)}
    ebook = get_ebook_by_id_or_slug(match)
    
    return ebook

@ebook.get(
    path='/slug/{slug}',
    name="Info ebook by slug",
    description="Info ebook by slug",
)
async def info_ebook_by_slug(slug):

    match = {"slug":slug}
    ebook = get_ebook_by_id_or_slug(match)
        
    # update view 
    ebook_view = client.ebook.find_one_and_update(
        {"_id":ObjectId(ebook["_id"])},
        {"$inc": {"views": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    if ebook_view:
        ebook["views"] = ebook_view["views"]

    return ebook

 
@ebook.post(
    path='/',
    name="Create ebook",
    description="Create ebook",
)
async def create_ebook(ebook: Ebook, auth: dict = Depends(validate_token)):

    ebook = ebook.dict()
    ebook["slug"] = gen_slug_radom_string(ebook["name"], 8)
    ebook['created_by'] = ObjectId(auth)
    ebook['updated_by'] = ObjectId(auth)

    ebook_create = client.ebook.insert_one(ebook)

    if ebook["categories"]:
        client.category.update_many({"_id": {"$in": ebook["categories"]}},{"$push": {"ebooks": ebook["_id"]}})
    
    categories = list(client.category.find({"_id": {"$in": ebook["categories"]}}, {"_id": { "$toString": "$_id" }, "name": 1, "name_en":1, "description":1}))
    ebook["_id"] = str(ebook_create.inserted_id)
    ebook["categories"] = categories
    del ebook['created_by'], ebook['updated_by']

    return ebook


@ebook.put(
    path='/{id}',
    name="update ebook",
    description="update ebook",
) 
async def update_ebook(id, ebook: Ebook, auth: dict = Depends(validate_token)):

    ebook_exist = client.ebook.find_one({"_id":ObjectId(id)})
    if not ebook_exist:
        raise HTTPException(404, detail="Ebook not found!")
    
    ebook= ebook.dict()
    ebook['updated_by'] = ObjectId(auth)

    if ebook_exist["name"]!= ebook["name"]:
        ebook["slug"] = gen_slug_radom_string(ebook["name"], 8)

    if "categories" in ebook:
        category_ids = ebook["categories"]
        category_exist_ids = ebook_exist["categories"]
        is_equal,list_add,list_delete = compare_old_to_new_list(category_ids, category_exist_ids)
        if not is_equal:
            if len(list_add):
                list_add = [ObjectId(cate) for cate in list_add]
                client.category.update_many({"_id": {"$in": list_add}},{"$push": {"ebooks": id}})
            if len(list_delete):
                list_delete = [ObjectId(cate) for cate in list_delete]
                client.category.update_many({"_id": {"$in": list_delete}},{"$pull": {"ebooks": id}})

    categories = list(client.category.find({"_id": {"$in": category_ids}}, {"_id": { "$toString": "$_id" }, "name": 1, "name_en":1, "description":1}))

    ebook = client.ebook.find_one_and_update({"_id":ObjectId(id)},{
        "$set":ebook
    }, return_document = ReturnDocument.AFTER)

    ebook["_id"] = str(ebook["_id"])
    ebook["categories"] = categories
    del ebook['created_by'], ebook['updated_by']

    return ebook

@ebook.delete(  
    path='/{id}',
    name="Delete ebook",
    description="Delete ebook",
)
async def delete_ebook(id, auth: dict = Depends(validate_token)):
    ebook = client.ebook.find_one({"_id":ObjectId(id)})
    if not ebook:
        raise HTTPException(404, detail="Ebook not found!")
    
    # if auth["role"] !=1:
    #     raise HTTPException(403, detail="No permission!")


    if len(ebook["categories"]):
        client.category.update_many({"_id": {"$in": ebook["categories"]}},
                                    {"$pull": {"ebooks": ObjectId(id)}})
        
    client.ebook_comment.delete_many({"ebook_id":ObjectId(id)})
    client.ebook_rate.delete_many({"ebook_id":ObjectId(id)})

    client.ebook.find_one_and_delete({"_id":ObjectId(id)})
    
    return JSONResponse(content={"message":"Delete success"}, status_code=200)


@ebook.post(  
    path='/rate',
    name="Rate ebook",
    description="Rate ebook",
)
async def rate_ebook(rate: EbookRate, auth: dict = Depends(validate_token)):

    rate= rate.dict()
    rate["user_id"] = ObjectId(auth)  
    ebook = client.ebook.find_one({"_id":rate["ebook_id"]})

    if not ebook:
        raise HTTPException(404, detail="Ebook not found!")
    
    ebook_rate= client.ebook_rate.insert_one(rate)

    rate["_id"] = str(ebook_rate.inserted_id)
    rate["ebook_id"] = str(rate["ebook_id"])
    del rate["user_id"]

    return rate

@ebook.get(  
    path='/check_rate/{ebook_id}',
    name="Rate ebook",
    description="Rate ebook",
)
async def check_rate(ebook_id, auth: dict = Depends(validate_token)):

    ebook = client.ebook.find_one({"_id":ObjectId(ebook_id)})

    if not ebook:
        raise HTTPException(404, detail="Ebook not found!")
    
    default_rate={"rate": 0, "_id": None, "is_rate": False}
    ebook_rate = client.ebook_rate.find_one({"ebook_id": ObjectId(ebook_id), "user_id": ObjectId(auth)},
                                            {"rate": 1, "_id": {"$toString": "$_id"}})
    if ebook_rate:
        ebook_rate["is_rate"] = True
        return ebook_rate

    return default_rate

@ebook.get(  
    path='/download/{ebook_id}',
    name="Download ebook",
    description="Download ebook",
)
async def download_ebook(ebook_id):

    ebook = client.ebook.find_one({"_id":ObjectId(ebook_id)})

    if not ebook:
        raise HTTPException(404, detail="Ebook not found!")
    
    client.dashboard.find_one_and_update({"key":DASHBOARD},{"$inc": {"downloads": 1}},upsert=True)

    return {"message": "Download ebook sucess"}


@ebook.get(  
    path='/read_ebook/{ebook_id}',
    name="Reads ebook online",
    description="Reads ebook online",
)
async def reads_ebook(ebook_id):

    ebook = client.ebook.find_one({"_id":ObjectId(ebook_id)})

    if not ebook:
        raise HTTPException(404, detail="Ebook not found!")
    
    client.dashboard.find_one_and_update({"key":DASHBOARD},{"$inc": {"online_reads": 1}},upsert=True)

    return {"message": "Reads ebook online"}


@ebook.get(  
    path='/crawl_data/{ebook_name}',
    name="Crawl data",
    description="Crawl data",
)
async def craw_data(ebook_name):

    data = crawl_data(ebook_name)
   
    return data



