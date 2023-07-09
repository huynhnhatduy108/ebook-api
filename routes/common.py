from fastapi import APIRouter, Depends, HTTPException
from config.constant import DASHBOARD
from functions.auth import generate_token, validate_token
from config.db import client

common = APIRouter() 

@common.get(  
    path='/dashboard/',
    name="Get info dashboard",
    description="Get info dashboard",
)
async def get_info_dashboard(auth = Depends(validate_token)):

    # count category
    categories = client.category.count_documents({})

    # count ebook commment
    ebook_comments = client.ebook_comment.count_documents({})


    # count post commment
    post_comments = client.post_comment.count_documents({})

    # post
    posts = list(client.post.aggregate([
                {
                    "$group": {
                        "_id": 1,
                        "views": { "$sum": "$views" },
                        "count": { "$sum": 1 }
                    }
                }
        ]))
    p_views =0
    p_count =0
    if len(posts) > 0:
        p_views = posts[0]["views"]
        p_count = posts[0]["count"]
        
    # users
    users = client.user.count_documents({})

    # noti
    noti = client.notification.count_documents({})

    # Ebook
    ebooks = list(client.ebook.aggregate([
                {
                    "$group": {
                        "_id": 1,
                        "views": { "$sum": "$views" },
                        "downloads": { "$sum": "$downloads" },
                        "count": { "$sum": 1 }
                    }
                }
        ]))
    
    b_views =0
    b_downloads =0
    b_count =0

    if len(ebooks) > 0:
         b_views = ebooks[0]["views"]
         b_downloads = ebooks[0]["downloads"]
         b_count = ebooks[0]["count"]

    dashboard = client.dashboard.find_one({"key":DASHBOARD})

    data ={
        "ebook_count": {
            "count":b_count,
            "views":b_views,
            "downloads":b_downloads,
            "comments": ebook_comments,
        },
         "post_count": {
            "count":p_count,
            "views":p_views,
            "comments":post_comments,
        },
        "user_count": users,
        "category_count": categories,
        "noti_count":noti,
        "views":dashboard["views"],
        "downloads":dashboard["downloads"],
        "online_reads":dashboard["online_reads"],
    }
   
    return data


@common.post(  
    path='/create/',
    name="create dashboard",
    description="create dashboard",
)
async def create_dashboard():
    dashboard = client.dashboard.find({"key":DASHBOARD})

    if dashboard:
        raise HTTPException(400, detail="Dashboard was existed!")
     
    data ={
            "key":DASHBOARD,
            "views":0,
            "dowloads":0,
            "online_reads":0,
        }
    client.dashboard.insert_one(data)

    return {"message":"Dashboard create success"}

@common.get(  
    path='/travel/',
    name="Travell to website",
    description="Travell to website",
)
async def travel_to_dashboard():
    client.dashboard.find_one_and_update({"key":DASHBOARD},{"$inc": {"views": 1}},upsert=True,)
    return {"message":"Well common to Ebook Free"}



