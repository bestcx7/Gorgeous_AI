from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.params import Body
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix='/posts' ,
    tags=['posts']
)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None
 
 
while True:
     
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi',
                                user='postgres', password='136552', 
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)
    

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, 
            {"title": "favourite food", "content": "I like pizza", "id": 2}]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p
    
        
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

@router.get("/")
def root():
    return {"message": "welcome to my api!!!!!"}


@router.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    
    posts = db.query(models.Post).all()
    return {"data": posts}


@router.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}


@router.post("/createposts", status_code=status.HTTP_201_CREATED)
def creat_posts(post: Post, db: Session = Depends(get_db)):
    #cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #               (post.title, post.content, post.published))
    #new_post = cursor.fetchone()
    #conn.commit()
    new_post = models.Post(
        title=post.title, content=post.content, published=post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return {"data": new_post}
# title str, content str


@router.get("/latest")
def get_latest_post():
    post = my_posts[len(my_posts)-1]
    return {"detail": post}


@router.get("/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * from posts WHERE id = %s""", (str(id)))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).all()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
        #   response.status_code = status.HTTP_404_NOT_FOUND
        #  return {'message': f"post with id: {id} was not found"}
    return {"post_detail": post}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # deleting post
    # find the index in the array that has required ID
    # my_posts.pop(index)
    # cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id)))
    # delete_post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id)
    
    
    if post.first() == None:
        return HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                             detail=f"post with id: {id} does not exist")
        
    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}")
def update_post(id: int, post: Post, db: Session = Depends(get_db) ):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, 
                  # (post.title, post.content, post.published, str(id)))
    # update_post = cursor.fetchone()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    post = post_query.first()
    
    if post == None:
        return HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                             detail=f"post with id: {id} does not exist")
        
    post_query.update(post.dict(), synchronize_session=False)
    
    db.commit()

    return {"data": post_query.first()}
