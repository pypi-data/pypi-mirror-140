from .qloader import qLoad
from .llibb import Crawler
import json
from .loadFlwd import selectFol, selectFol2, follow, login_
import random
import time

followed = []
logfile = open("followed.txt", "r")
followed = logfile.read().splitlines()
logfile.close()
logfile = open("followed.txt", "a")

stack = []

def getId(d):
    if "user" in d:
        return d["user"]["id"]
    elif "follow" in d:
        return d["follow"]["id"]
    else:
        return None

def addFollow(s):
    if s == None:
        return
    if len(stack) < 2500:
        if(s not in followed):
            followed.append(s)
            logfile.write(f"\n{s}")
            stack.append(s)

def selectList(t="entrystory", v={}):
    crawler = Crawler()

    a = crawler.postPage({
        "url": "https://playentry.org/graphql",
        "header": {
            "content-type": "application/json"
        },
        "body": json.dumps({
            "query": qLoad(f"select_{t}"),
            "variables":v
        })
    })

    j = json.loads(a)

    l = j["data"]["discussList"]["list"]

    return l

def selectES(n=3):
    return selectList("entrystory", {
        "category": "free",
        "searchType": "scroll",
        "term": "all",
        "discussType": "entrystory",
        "pageParam": {
            "display": n,
            "sort": "created"
        }
    })

def selectKT(n=3):
    return selectList("knowtips", {
        "category": "tips",
        "searchType": "scroll",
        "term": "all",
        "pageParam": {
            "display": n,
            "sort": "created"
        }
    })

def selectQA(n=3):
    return selectList("qna", {
        "category": "qna",
        "searchType": "page",
        "term": "all",
        "pageParam": {
            "start": 0,
            "display": n,
            "sort": "created"
        }
    })


def frame():
    if random.randint(0, 9) == 0:
        qrt = random.randint(1, 2)
    else:
        qrt = 0
    l = (selectES if qrt == 0 else selectKT if qrt == 1 else selectQA)()
    for i in l:
        addFollow(getId(i))
    
    qrt = random.randint(0, 1)
    if qrt == 0:
        l = selectFol()
    else:
        l = selectFol2()

    j = random.choice(l)
    qrt = random.randint(0, 1)
    if qrt == 0:
        l = selectFol(lid=getId(j))
    else:
        l = selectFol2(lid=getId(j))
    
    for i in l:
        addFollow(getId(i))

def followLast(n=5):
    if len(stack) > 0:
        t = min(n, len(stack))
        for i in range(t):
            j = stack.pop()
            follow(j)
            print(f"https://playentry.org/profile/{j} 님을 팔로우했어요!")

def run():
    while True:
        try:
            frame()
            if len(stack) > 1000:
                followLast(50)
            elif len(stack) > 100:
                followLast(15)
            else:
                followLast()
        except Exception as e:
            print(e)
        time.sleep(0.5)

def login(usr, pas):
    login_(pas, usr)
    

