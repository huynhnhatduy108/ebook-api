from fastapi import APIRouter, Depends, HTTPException
from functions.auth import generate_token, validate_token
from functions.function import compare_old_to_new_list, gen_slug_radom_string
from models.ebook import Ebook
from config.db import client
from schemas.ebook import EbookQueryParams, EbookSlugParams, serializeDict, serializeList
from bson import ObjectId
from fastapi.responses import JSONResponse
from pymongo import ReturnDocument, UpdateOne

ebook = APIRouter() 

@ebook.get(
    path='/',
    name="List ebook",
    description="Get list ebook",
)
async def list_ebooks(param:EbookQueryParams = Depends()):
    query = {}
    page = param.page
    page_size = param.page_size
    skip = page * page_size - page_size;

    if "keyword" in dict(param):
        if param.keyword:
            query["$or"] = [{"name":{"$regex" : param.keyword, '$options': 'i'}},
                            {"name_en":{"$regex" : param.keyword, '$options': 'i'}},
                            {"intro":{"$regex" : param.keyword, '$options': 'i'}},
                            {"intro_en":{"$regex" : param.keyword, '$options': 'i'}},
                            ]
    if "category" in dict(param):
        if param.category:
            query["categories"] = param.category

    ebook = client.ebook.find(query,{"deleted_flag":0})
    ebook = ebook.skip(skip).limit(page_size)
    total_record = client.ebook.count_documents(query)

    ebook = serializeList(ebook)
    data ={
        "items": ebook,
        "page":page,
        "page_size":page_size,
        "total_record":total_record
    }
    return data


@ebook.get(
    path='/{id}',
    name="Info ebook by id",
    description="Info ebook by id",
)
async def info_ebook_by_id(id:str):
    ebook = client.ebook.find_one({"_id":ObjectId(id)},{"deleted_flag":0})

    if not ebook:
        raise HTTPException(404, detail="Ebook not found!")
    
    ebook = serializeDict(ebook)

    return ebook

@ebook.get(
    path='/slug/{slug}',
    name="Info ebook by slug",
    description="Info ebook by slug",
)
async def info_ebook_by_slug(slug):
    ebook = client.ebook.find_one({"slug":slug},{"deleted_flag":0})

    if not ebook:
        raise HTTPException(404, detail="Ebook not found!")
    
    # update view 
    ebook_view = client.ebook_view.find_one_and_update(
        {"ebook_id": str(ebook["_id"])},
        {"$inc": {"views": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    if ebook_view:
        ebook["views"] = ebook_view["views"]
    ebook = serializeDict(ebook)

    return ebook

 
@ebook.post(
    path='/',
    name="Create ebook",
    description="Create ebook",
)
async def create_ebook(ebook: Ebook, auth: dict = Depends(validate_token)):

    ebook = ebook.dict()
    ebook["slug"] = gen_slug_radom_string(ebook["name"], 8)

    category_ids = []
    categories = []
    if "categories" in ebook:
        if ebook["categories"]:
            category_ids = [ObjectId(category) for category in ebook["categories"]]
            categories = client.category.find({"_id": {"$in": category_ids}})
            categories = [{"_id":str(cate["_id"]), "name":cate["name"]} for cate in categories]
            ebook["categories"] = categories
        else:
            ebook["categories"]=[]

    ebook_create = client.ebook.insert_one(ebook)
    ebook["_id"] = str(ebook_create.inserted_id)

    client.ebook_view.insert_one({"ebook_id":ebook["_id"], "views": 0 })
    client.ebook_download.insert_one({"ebook_id":ebook["_id"], "downloads": 0 })

    if categories:
        client.category.update_many({"_id": {"$in": category_ids}},{"$push": {"ebooks": ebook["_id"]}})
    
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
    if ebook_exist["name"]!= ebook["name"]:
        ebook["slug"] = gen_slug_radom_string(ebook["name"], 8)

    if "categories" in ebook:
        category_ids = [ObjectId(category) for category in ebook["categories"]]
        category_exist_ids = [ObjectId(category["_id"]) for category in ebook_exist["categories"]]
        list_add,list_delete = compare_old_to_new_list(category_ids, category_exist_ids)
        
        if len(list_add):
            list_add = [ObjectId(cate) for cate in list_add]
            client.category.update_many({"_id": {"$in": list_add}},{"$push": {"ebooks": id}})
        if len(list_delete):
            list_delete = [ObjectId(cate) for cate in list_delete]
           
            client.category.update_many({"_id": {"$in": list_delete}},{"$pull": {"ebooks": id}})

        categories = client.category.find({"_id": {"$in": category_ids}}, {"_id": 1, "name": 1})
        categories = [{"_id": str(cate["_id"]), "name": cate["name"]} for cate in categories]
        ebook["categories"] = categories

    ebook = client.ebook.find_one_and_update({"_id":ObjectId(id)},{
        "$set":ebook
    }, return_document = ReturnDocument.AFTER)


    ebook["_id"] = str(ebook["_id"])

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

    category_ids = [ObjectId(cate["_id"]) for cate in ebook["categories"]]
    if len(category_ids):
        client.category.update_many({"_id": {"$in": category_ids}},
                                    {"$pull": {"ebooks": id}})

    client.ebook.find_one_and_delete({"_id":ObjectId(id)})
    return JSONResponse(content={"message":"Delete success"}, status_code=200)
