import requests
import time
import re
import sqlalchemy
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String

engine = create_engine('mysql://root:@localhost/henry', pool_recycle=3600)
Base = declarative_base()
session = Session(engine)
class Response(Base):
     __tablename__ = 'Response'

     id = Column(Integer, primary_key=True)
     trigger = Column(String)
     response = Column(String)
     def __init__(self, trigger,response):
         self.trigger = trigger
         self.response = response

     def __repr__(self):
        return "<Response(trigger='%s', response='%s')>" % (
                             self.trigger, self.response)

API_KEY = os.environ['HENRY_API_KEY']

dict = {}
def parse_response(json):
    if 'text' in json['message']:
        match = re.search(r'(\w+):(\w+):(.+)', json['message']['text'])
        if match is not None:
            if(match.group(1) == "add"):
                pattern = match.group(2)
                answer = match.group(3)
                if len(pattern)> 2:
                    dict[pattern] = answer
                    session.add(Response(pattern,answer))
                    session.commit()
        for key in dict.keys():
            if key in json['message']['text']:
                requests.get("https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(API_KEY, json['message']['chat']['id'], dict[key]))


def loop(id = 0):
    data = requests.get("https://api.telegram.org/bot{}/getUpdates?offset={}&timeout=30".format(API_KEY, id))
    json = data.json()
    result = json['result']
    if len(result) > 0:
        id = result[0]['update_id']
        parse_response(result[0])
    time.sleep(0.2)
    loop(id + 1)

if __name__ == '__main__':
    q = session.query(Response).all()
    for response in q:
        dict[response.trigger] = response.response
    loop()

