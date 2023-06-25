import os
from dotenv import load_dotenv
load_dotenv()

LOCAL_PROVIDER ="LOCAL"
FACEBOOK_PROVIDER ="FACEBOOK"
GOOGLE_PROVIDER ="GOOGLE"

MALE ="MALE"
FEMALE ="FEMALE"

DASHBOARD ="DASHBOARD"

DEFAULT_AVATAR_MAN = os.environ.get('DEFAULT_AVATAR_MAN',"https://firebasestorage.googleapis.com/v0/b/ebook-389008.appspot.com/o/default%2Fvavatar_man.png?alt=media&token=969bbe0a-d5b5-483a-8230-378bf7119399")
DEFAULT_AVATAR_WOMEN = os.environ.get('DEFAULT_AVATAR_WOMEN', "https://firebasestorage.googleapis.com/v0/b/ebook-389008.appspot.com/o/default%2Favatar_women.jpeg?alt=media&token=a976a603-7048-4347-a6bf-b9a84cedf8e3")

TIKI_DOMAIN = os.environ.get('TIKI_DOMAIN',"https://tiki.vn/")
TIKI_API = os.environ.get('TIKI_API',"https://tiki.vn/api/v2/")

SHOPEE_DOMAIN = os.environ.get('SHOPEE_DOMAIN',"https://shopee.vn/")
SHOPEE_API = os.environ.get('SHOPEE_API')

DATABASE_URL = os.environ.get('DATABASE_URL',"mongodb+srv://nest:nest@nest-cluster.gapiqqm.mongodb.net/ebook?retryWrites=true&w=majority")

CLOUDINARY_CLOUD_URL= os.environ.get('CLOUDINARY_CLOUD_URL')
FIREBASE_CLOUD_URL=os.environ.get("FIREBASE_CLOUD_URL")

# UPLOAD PATH
BOOK_THUMBNAIL_PATH="/ebook%2Fthumbnail%2F"
BOOK_PDF_PATH="/ebook%2Fpdf%2F"
BOOK_EPUB_PATH="/ebook%2Fepub%2F"
BOOK_MOBI_PATH="/ebook%2Fmobi%2F"
BOOK_AZW_PATH="/ebook%2Fazw%2F"
BOOK_PRC_PATH="/ebook%2FpRC%2F"


CATEGORY_PATH ="/category%2F"
POST_PATH=""
USER_PATH =""
DEFAULT_PATH =""


VIETNAMESE="VIETNAMESE"
ENGLISH ="ENGLISH"
LANGUAGES ={
    VIETNAMESE:VIETNAMESE,
    ENGLISH:ENGLISH
}