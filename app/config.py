import json
from pydantic import BaseModel


class Config(BaseModel):
    dbname: str
    user: str
    password: str
    host: str
    port: str


with open("./config.json", "r") as file:
    data = json.load(file)

config = Config(**data)
