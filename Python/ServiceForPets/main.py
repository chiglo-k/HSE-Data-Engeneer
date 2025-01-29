from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class DogType(str, Enum):
    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"

class Dog(BaseModel):
    name: str
    pk: int
    kind: DogType

class Timestamp(BaseModel):
    id: int
    timestamp: int

dogs_db = {
    0: Dog(name='Bob', pk=0, kind=DogType.terrier),
    1: Dog(name='Marli', pk=1, kind=DogType.bulldog),
    2: Dog(name='Snoopy', pk=2, kind=DogType.dalmatian),
    3: Dog(name='Rex', pk=3, kind=DogType.dalmatian),
    4: Dog(name='Pongo', pk=4, kind=DogType.dalmatian),
    5: Dog(name='Tillman', pk=5, kind=DogType.bulldog),
    6: Dog(name='Uga', pk=6, kind=DogType.bulldog)
}

post_db = [
    Timestamp(id=0, timestamp=12),
    Timestamp(id=1, timestamp=10)
]

@app.get('/')
def root():
    return {"message": "Welcome to API for ya Dog!"}

@app.post('/post')
def get_post():
    return post_db

@app.get('/dog')
def get_dogs(kind: DogType = None):
    if kind:
        return [dog for dog in dogs_db.values() if dog.kind == kind]
    return list(dogs_db.values())

@app.post('/dog')
def create_dog(dog: Dog):
    if dog.pk in dogs_db:
        return {'error': 'PK is already connected with another dog.'}
    dogs_db[dog.pk] = dog
    return dog

@app.get('/dog/{pk}')
def got_dog_by_pk(pk: int):
    dog = dogs_db.get(pk)
    if not dog:
        return {"error": "Dog not found."}
    return dog

@app.patch('/dog/{pk}')
def update_dog(pk: int, dog: Dog):
    if pk not in dogs_db:
        return {"error": "Dog not found."}
    dogs_db[pk] = dog
    return dog
