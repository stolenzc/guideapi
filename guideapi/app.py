from api import API

app = API()

# 通过装饰器关联路由和方法
@app.route("/home")
def home(request, response):
    response.text = "This is Home"

# 路由中可以有变量，对应的方法也需要有对应的参数
@app.route("/hello/{name}")
def hello(requst, response, name):
    response.text = f"Hello, {name}"

# 可以装饰类
@app.route("/book")
class BooksResource(object):
    def get(self, req, resp):
        resp.text = "Books Page"

def handler1(req, resp):
    resp.text = "handler1"
# 可以直接通过add_route方法添加   
app.add_route("/handler1", handler1)
