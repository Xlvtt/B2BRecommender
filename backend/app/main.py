from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from recommender import Recommender

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class BuyerCreate(BaseModel):
    region: str


recommender = Recommender()


@app.get("/buyers")
async def get_buyers():
    return recommender.data.get_buyers()#.to_dict(orient='records')


@app.post("/buyers")
async def create_buyer(buyer: BuyerCreate):
    # Логика создания
    return {"message": "Buyer created"}


@app.get("/recommendations/{buyer_id}")
async def get_recommendations(buyer_id: str):
    return recommender.recommend(buyer_id)
