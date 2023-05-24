from fastapi import FastAPI,HTTPException,Request
from bson import ObjectId
import motor.motor_asyncio
from fastapi.middleware.cors import CORSMiddleware
import pydantic
import os
from dotenv import load_dotenv
from datetime import datetime,timedelta
import uvicorn
import json
import requests
import pytz
import re


app = FastAPI()

#FastAPI (Uvicorn) runs on 8000 by Default


load_dotenv() 
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGO_CONNECTION_STRING')) #Hiding Database URL 
db = client.audiogramdb

pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#POST Because we actually want a record of the previous ones  
@app.post("/api/state",status_code=201) #cool that I changed it to post ?
async def set_state(request:Request):
    
    audioreading = await request.json() #Processes input from the Microcontroller's Sent HTTP Request
    audioreading["datetime"]=(datetime.now()+timedelta(hours=-5)).strftime('%Y-%m-%dT%H:%M:%S') #Appends Current Date Time to Entry to be made in database
    newaudioreading = await db["states"].insert_one(audioreading) #Inserts the entry into the database
    updatedaudioreading = await db["states"].find_one({"_id": newaudioreading.inserted_id }) #updated_tank.upserted_id
    if newaudioreading.acknowledged == True:
        return updatedaudioreading
    raise HTTPException(status_code=400,detail="Issue")

