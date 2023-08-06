from .llibb import Crawler
from .qloader import qLoad
import json
from .login import loginAs

cookie = None

def selectFol(n=100, lid="621b0b7c294723001b1bc390"):
    if lid == None:
        return
    crawler = Crawler()

    a = crawler.postPage({
        "url": "https://playentry.org/graphql",
        "header": {
            "content-type": "application/json"
        },
        "body": json.dumps({
            "query": qLoad(f"select_followings"),
            "variables": {
                "user": lid,
                "pageParam":  {
                    "display": n
                }
            }
        })
    })

    j = json.loads(a)

    l = j["data"]["followings"]["list"]

    return l

def selectFol2(n=100, lid="621b0b7c294723001b1bc390"):
    if lid == None:
        return
    crawler = Crawler()

    a = crawler.postPage({
        "url": "https://playentry.org/graphql",
        "header": {
            "content-type": "application/json"
        },
        "body": json.dumps({
            "query": qLoad(f"select_followers"),
            "variables": {
                "user": lid,
                "pageParam":  {
                    "display": n
                }
            }
        })
    })

    j = json.loads(a)

    l = j["data"]["followers"]["list"]

    return l

def follow(lid: str):
    crawler = Crawler()
    crawler.loadCookiesFromStr(cookie)

    a = crawler.postPage({
        "url": "https://playentry.org/graphql",
        "header": {
            "content-type": "application/json"
        },
        "body": json.dumps({
            "query": qLoad(f"follow"),
            "variables": {
                "user": lid
            }
        })
    })

    j = json.loads(a)

    l = j["data"]

    return l

def login_(p, u):
    global cookie
    cookie = loginAs(p, u)