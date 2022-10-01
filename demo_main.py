from fastapi import FastAPI
from enum import Enum

app = FastAPI()

## The enum members have names and values. The name of ModelName.alexnet is alexnet,
## the value of ModelName.alexnet is "alexnet"
## ModelName.alexnet.name == alexnet
class ModelName(str, Enum):
    alexnet = "alexnet"
    mustafa = "king"
    resnet = "resnet"
    lenet = "lenet"

print(ModelName.mustafa)
print(ModelName.mustafa.name == "mustafa")
print(ModelName.mustafa.value == "king")
for models in ModelName:
    print(models.name)



@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}


@app.get("/models/{model_name}")
##Declare a path parameter¶
##Then create a path parameter with a type annotation using the enum class you created (ModelName):
async def get_model(model_name: ModelName):
    if model_name is ModelName.mustafa:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


## multiple path and query parameters
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str, 
        q: str | None = None, short: bool = False):

    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

## required query parameters
## /items/foo is not enough, there must be two strings combined to complete item
## http://127.0.0.1:8000/items/foo-item?needy=sooooneedy
@app.get("/items/couple/{item_id}")
async def read_user_item_couple(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item

## giving a default value
@app.get("/items/default/{item_id}")
async def read_user_item(item_id: str, needy: str, 
        skip: int = 0, limit: int | None = None):

    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item


###### REQUEST BODY #######
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})

    return item_dict


class Itemx(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    ## here the tags will become unique strings
    tags: set[str] = set()



@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Itemx):
    results = {"item_id": item_id, "item": item}
    return results


class Items(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


@app.put("/itemsx/{item_id}")
async def update_item(item_id: int, item: Items):
    results = {"item_id": item_id, "item": item}
    return results


#### RESPONSE MODEL ####
from pydantic import EmailStr

class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    return user


### Response model encoding ###
class Itemy(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5
    tags: list[str] = []


itemsy = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get("/itemsy/{item_id}", response_model=Itemy, response_model_exclude_unset=True)
async def read_itemy(item_id: str):
    return itemsy[item_id]

### Form Data ###

from fastapi import Form, UploadFile, File

@app.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}

## not able to show in the api docs
app.post("/upload/")
async def create_file(
    file: bytes = File(), 
    fileb: UploadFile = File(), 
    token: str = Form() 
    ):

    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }

### Exception Handle ###
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.get("/itemsmx/{item_id}")
async def read_itemmx(item_id: int):
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}


### JSON compatible ###
from datetime import datetime
from fastapi.encoders import jsonable_encoder

fake_db = {}


class Itemdf(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None



@app.put("/itemssda/{id}")
def update_item(id: str, item: Itemdf):
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data
    return fake_db[id]