#pylint: disable=no-name-in-module
#pylint: disable=no-self-argument

from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pprint
import bcrypt
import base64
import hashlib

#VERY UNSAFE#
client = MongoClient("mongodb+srv://michalpc:test1234@simple-user-login-app-d.ki5ky.mongodb.net/db?retryWrites=true&w=majority")
db = client['db']
collection = db['users']

app = FastAPI()

origins = [ "*" ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    username: str
    password: str

class NewUser(BaseModel):
    username: str
    password: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/exists/")
async def usernameEmpty():
    return {"err": "No username provided"}

@app.get("/exists/{username}")
async def userExists(username):
    userExists = collection.find({"username": username})
    if(userExists.count() == 1):
        return {"exists": True}
    return {"exists": False}

@app.post("/login/")
async def login(user: User):
    userExists = collection.find({"username": user.username})
    
    if(userExists.count() == 1):
        encodedPassword = user.password.encode('utf-8')
        if(bcrypt.checkpw(encodedPassword, userExists[0]['password'])):
            return {"login": True}
    raise HTTPException(status_code=401, detail="Provided details are incorrect!")

@app.post("/signup/")
async def signUp(newUser: NewUser):
    userExists = collection.find({"username": newUser.username})

    if(userExists.count() == 1):
        raise HTTPException(status_code=422, detail="Username has been taken!")
    else:
        collection.insert({
            "username": newUser.username,
            "password": bcrypt.hashpw(newUser.password.encode("utf-8"), bcrypt.gensalt(12))
        })
        return {"signup": True}
