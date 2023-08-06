from lib import Crawler
import json
from qloader import qLoad

from settings import sec

crawler = Crawler()

a = crawler.postPage({
    "url": "https://playentry.org/graphql",
    "header": {
        "content-type": "application/json"
    },
    "body": json.dumps({
        "query": qLoad("login"),
        "variables":{
            "password": sec['pwd'],
            "username": sec['usr'],
            "rememberme": True
        }
    })
})

cookie: str = crawler.exportCookies()