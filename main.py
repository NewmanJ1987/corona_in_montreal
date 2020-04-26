import uvicorn
import uuid
from fastapi import FastAPI, Query
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timedelta
from typing import List, Optional
import GetOldTweets3


class Comment(BaseModel):
    id: str
    name: str
    comment: str
    date: Optional[datetime] = datetime.now()
    edited: Optional[bool] = False
    modified_date: Optional[datetime] = None
    upvote: Optional[int] = 0


class CreateComment(BaseModel):
    name: str
    comment: str


class TwitterComment(BaseModel):
    text: str
    name: str
    date: str
    permalink: HttpUrl
    reply: bool = False
    hashtags : str 
    favorites: int
    replies: int
    retweets: int


app = FastAPI()
comments: List[Comment] = []


def find_comment(comment_id):
    for index, comment in enumerate(comments):
        if comment.id == comment_id:
            return index


def get_tweets(username, num_tweets):
    tweetCriteria = GetOldTweets3.manager.TweetCriteria().setUsername(username)\
        .setSince(str(datetime.now().date() - timedelta(days=1)))\
        .setMaxTweets(num_tweets)
    return GetOldTweets3.manager.TweetManager.getTweets(tweetCriteria)
    
def process_raw_tweets(username, raw_tweets):
    tweets = []
    for tweet in raw_tweets:
        tweets.append(TwitterComment(
            name = username,
            text = tweet.text,
            date = tweet.formatted_date,
            permalink = tweet.permalink,
            reply = True if tweet.to != '' else False,
            hashtags = tweet.hashtags,
            favorites = tweet.favorites,
            replies = tweet.replies,
            retweets = tweet.retweets)
        )
    return tweets

@app.get("/tweets", response_model=List[TwitterComment])
async def get_latest_tweets(twitter_handler:str = Query("Aaron_Derfel"), num_tweets:int= Query(20)):
    raw_tweets = get_tweets(twitter_handler, num_tweets)   
    processed_tweets= process_raw_tweets(twitter_handler, raw_tweets)
    return processed_tweets


@app.get("/videos")
async def get_latests_youtube():
    return []


@app.get("/stats")
async def get_stats():
    return []


@app.get("/comment", response_model=List[Comment])
async def get_comment():
    return comments


@app.post("/comment", response_model=Comment)
async def create_comment(public_comment: CreateComment):
    comment = Comment(
        id=str(uuid.uuid4()).replace('-', ''),
        name=public_comment.name,
        comment=public_comment.comment
    )
    comments.append(comment)
    return comment


@app.put("/comment/{comment_id}")
async def update_comment(comment_id, comment: CreateComment):
    index = find_comment(comment_id)
    if index is not None:
        comments[index].name = comment.name
        comments[index].comment = comment.comment
        comments[index].modified_date = datetime.now()
        comments[index].edited = True


@app.put("/comment/{comment_id}/upvote")
async def upvote_comment(comment_id):
    index = find_comment(comment_id)
    if index is not None:
        comments[index].upvote += 1

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
