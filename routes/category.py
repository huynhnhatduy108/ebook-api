from fastapi import APIRouter, Depends, HTTPException
from functions.auth import generate_token, validate_token
from functions.function import gen_slug_radom_string
from models.category import Category
from config.db import client
from schemas.category import CategoryQueryParams
from bson import ObjectId
from fastapi.responses import JSONResponse
from pymongo import ReturnDocument
import math

category = APIRouter() 

@category.get(
    path='/',
    name="List category",
    description="Get list category",
)
async def list_categories(param:CategoryQueryParams = Depends()):
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
                                        {"description":{"$regex" : param.keyword, '$options': 'i'}},
                                      ]       
                            }
            
            match_condition["$and"].append(keyword_scope)

    if "posts" in dict(param):
        if param.posts:
            cates_scope = {"categories._id":{"$in":param.posts} }
            match_condition["$and"].append(cates_scope)

    if "ebooks" in dict(param):
        if param.ebooks:
            cates_scope = {"tags":{"$in":param.ebooks} }
            match_condition["$and"].append(cates_scope)

    if "ordering" in dict(param):
        sort_condition=param.ordering

    pipline=[
                {
                    "$match": match_condition if match_condition["$and"] else {}
                },
                 {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "count.ebooks": { "$size": "$ebooks" },
                        "count.posts": { "$size": "$posts" }
                    }
                },
                 {
                    "$project": {
                        "deleted_flag": 0,
                        "ebooks":0,
                        "posts":0,
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
    

    result = client.category.aggregate(pipline)
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


@category.get(
    path='/full',
    name="List category full",
    description="Get list category full",
)
async def list_categories_full():
 
    pipline=[
                 {
                    "$addFields": {
                        "_id": { "$toString": "$_id" },
                        "count.ebooks": { "$size": "$ebooks" },
                        "count.posts": { "$size": "$posts" }
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
    

    result = client.category.aggregate(pipline)
    result = list(result)
   
    return result


@category.get(
    path='/{id}',
    name="Info category by id",
    description="Info category by id",
)
async def info_category_by_id(id:str):
    category = client.category.find_one({"_id":ObjectId(id)},
                                         { "_id": { "$toString": "$_id" },
                                           "name":1, 
                                           "name_en":1, 
                                           "thumbnail":1, 
                                           "description":1,
                                           "count.ebooks": { "$size": "$ebooks" },
                                           "count.posts": { "$size": "$posts" },
                                           "created_at": 1,
                                           "updated_at":1
                                           })

    if not category:
        raise HTTPException(404, detail="Category not found!")
    
    return category

 
@category.post(
    path='/',
    name="Create category",
    description="Create category",
)
async def create_category(category: Category, auth: dict = Depends(validate_token)):

    category = category.dict()
    category["ebooks"]=[]
    category["posts"]=[]

    category_create = client.category.insert_one(category)
    category["_id"] = str(category_create.inserted_id)

    return  category


@category.put(
    path='/{id}',
    name="update category",
    description="update category",
) 
async def update_category(id, category: Category, auth: dict = Depends(validate_token)):

    category_exist = client.category.find_one({"_id":ObjectId(id)})
    if not category_exist:
        raise HTTPException(404, detail="Category not found!")
    
    category= category.dict()
    const = client.category.find_one_and_update({"_id":ObjectId(id)},{
        "$set":category
    }, return_document = ReturnDocument.AFTER)

    const["_id"] = str(const["_id"])

    return const

@category.delete(  
    path='/{id}',
    name="Delete category",
    description="Delete category",
)
async def delete_category(id, auth: dict = Depends(validate_token)):

    # if auth["role"] !=1:
    #     raise HTTPException(403, detail="No permission!")

    category = client.category.find_one({"_id":ObjectId(id)})
    if not category:
        raise HTTPException(404, detail="Category not found!")
    
    if len(category["ebooks"]):
        client.ebook.update_many({"_id": {"$in": category["ebooks"]}},
                                 {"$pull": {"categories": ObjectId(id)}})
        
    if len(category["posts"]):
        client.post.update_many({"_id": {"$in": category["posts"]}},
                                {"$pull": {"categories": ObjectId(id)}})
    
    client.category.find_one_and_delete({"_id":ObjectId(id)})
    return JSONResponse(content={"message":"Delete success"}, status_code=200)
