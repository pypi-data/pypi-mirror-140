import requests, json

validURL = ["https://playentry.org/graphql", "https://playentry.org/rest/picture"]

def checkPostOptions(options):
    if "url" in options:
        url = options["url"].strip()
        if url not in validURL:
            return [False, "Url argument is not a valid graphql link"]
        else:
            if "header" not in options:
                return [False, "Missing header argument"]
            elif "body" not in options:
                return [False, "Missing body argument"]
            else:
                return [True, ""]
    else:
        return [False, "Missing url argument"]

class Crawler:
    def __init__(self) -> None:
        self.bot = requests.session()
        self.cookies = self.bot.cookies
        self.used = False

    def postPage(self, options, d401=False) -> str:
        if self.used == True:
            raise Exception("The current crawler is already used. Create a new crawler.")
        else:
            check = checkPostOptions(options)
            if check[0] == False:
                raise Exception(check[1])
            if d401:
                res = self.bot.post(options["url"], options["body"], headers=options["header"])
            else:
                res = self.bot.post(options["url"], options["body"], headers=options["header"])
            self.cookies = self.bot.cookies
            return res.text

    def postFile(self, options):
        if self.used == True:
            raise Exception("The current crawler is already used. Create a new crawler.")
        else:
            check = checkPostOptions(options)
            if check[0] == False:
                raise Exception(check[1])
            res = self.bot.post(options["url"], headers=options["header"], files=options["body"], data={})
            self.cookies = self.bot.cookies
            return res.status_code
    
    def saveCookies(self, filename: str) -> None:
        with open(filename, "w") as f:
            json.dump(requests.utils.dict_from_cookiejar(self.cookies), f)

    def loadCookies(self, filename: str) -> None:
        with open(filename, 'r') as f:
            cookies = requests.utils.cookiejar_from_dict(json.load(f))
            self.bot.cookies.update(cookies)

    def exportCookies(self) -> str:
        return json.dumps(requests.utils.dict_from_cookiejar(self.cookies))

    def loadCookiesFromStr(self, s: str):
        cookies = requests.utils.cookiejar_from_dict(json.loads(s))
        self.bot.cookies.update(cookies)
