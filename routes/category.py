from fastapi import APIRouter, Depends, HTTPException
from functions.auth import generate_token, validate_token
from functions.function import gen_slug_radom_string
from models.category import Category
from config.db import client
from schemas.category import CategoryQueryParams, serializeDict, serializeList
from bson import ObjectId
from fastapi.responses import JSONResponse
from pymongo import ReturnDocument

category = APIRouter() 

@category.get(
    path='/',
    name="List category",
    description="Get list category",
)
async def list_categories(param:CategoryQueryParams = Depends()):
    query = {}
    page = param.page
    page_size = param.page_size
    skip = page * page_size - page_size;

    if "keyword" in dict(param):
        if param.keyword:
            query["$or"] = [{"name":{"$regex" : param.keyword, '$options': 'i'}},
                            {"name_en":{"$regex" : param.keyword, '$options': 'i'}},
                            ]
    if "post" in dict(param):
        if param.post:
            post = param.post.split(",")
            query["categories"] ={"$in":post}
        
    if "ebook" in dict(param):
        if param.ebook:
            ebook = param.ebook.split(",")
            query["categories"] ={"$in":ebook}

    category = client.category.find(query,{"deleted_flag":0})
    category = category.skip(skip).limit(page_size)
    total_record = client.category.count_documents(query)

    category = serializeList(category)
    data ={
        "items": category,
        "page":page,
        "page_size":page_size,
        "total_record":total_record
    }
    return data


@category.get(
    path='/{id}',
    name="Info category by id",
    description="Info category by id",
)
async def info_category_by_id(id:str):
    category = client.category.find_one({"_id":ObjectId(id)},{"deleted_flag":0})

    if not category:
        raise HTTPException(404, detail="Category not found!")
    
    category = serializeDict(category)

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
        raise HTTPException(404, detail="category not found!")
    
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
    category = client.category.find_one({"_id":ObjectId(id)})
    if not category:
        raise HTTPException(404, detail="category not found!")
    
    # if auth["role"] !=1:
    #     raise HTTPException(403, detail="No permission!")
    client.category.find_one_and_delete({"_id":ObjectId(id)})
    return JSONResponse(content={"message":"Delete success"}, status_code=200)
