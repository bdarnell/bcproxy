import http.cookies
import json
import urllib.parse
import tornado.httpclient, tornado.ioloop, tornado.log, tornado.web

class LoginHandler(tornado.web.RequestHandler):
  async def post(self):
    client = tornado.httpclient.AsyncHTTPClient()
    headers = {}
    # The server appears to require these headers to be present.
    for k in ("Content-Type", "User-Agent"):
      if k in self.request.headers:
        headers[k] = self.request.headers[k]
    resp = await client.fetch(
      "https://www.babyconnect.com/Cmd?cmd=UserAuth",
      method="POST",
      body=self.request.body,
      headers=headers,
      follow_redirects=False,
      raise_error=False,
    )
    if resp.code != 302:
      self.set_status(500)
      self.finish(f"status code {resp.code}")
    else:
      # Parse the set-cookie header and put it in the request body
      cookie = http.cookies.SimpleCookie()
      for sc in resp.headers.get_list("Set-Cookie"):
        cookie.load(sc)
      if "seacloud1" in cookie:
        self.finish(dict(cookie=cookie["seacloud1"].coded_value))
      else:
        # TODO better error handling
        self.set_status(500)
        self.finish("cookie not found")
        print(resp)
        print(list(resp.headers.get_all()))


class StatusHandler(tornado.web.RequestHandler):
  async def post(self):
    client = tornado.httpclient.AsyncHTTPClient()
    headers = {}
    for k in ("Content-Type", "User-Agent"):
      if k in self.request.headers:
        headers[k] = self.request.headers[k]
    headers["Cookie"] = f"seacloud1={self.get_body_argument('cookie')}"
    body = urllib.parse.urlencode(dict(pdt=self.get_body_argument("pdt")))
    resp = await client.fetch(
      "https://www.babyconnect.com/CmdListW?cmd=StatusList",
      method="POST",
      body=body,
      headers=headers,
    )
    # TODO: Error handling
    self.finish(json.loads(resp.body))

if __name__ == '__main__':
  tornado.log.enable_pretty_logging()
  app = tornado.web.Application([
    ('/login', LoginHandler),
    ('/status', StatusHandler),
  ],
  client = tornado.httpclient.AsyncHTTPClient())
  app.listen(8080)
  tornado.ioloop.IOLoop.current().start()