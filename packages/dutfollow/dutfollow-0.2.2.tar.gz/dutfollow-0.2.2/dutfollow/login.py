from .llibb import Crawler
import json
from .qloader import qLoad

def loginAs(pwd, usr):
    crawler = Crawler()

    a = crawler.postPage({
        "url": "https://playentry.org/graphql",
        "header": {
            "content-type": "application/json"
        },
        "body": json.dumps({
            "query": qLoad("login"),
            "variables":{
                "password": pwd,
                "username": usr,
                "rememberme": True
            }
        })
    })

    cookie: str = crawler.exportCookies()
    return cookie