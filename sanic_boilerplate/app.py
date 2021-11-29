from sanic import Sanic
from sanic import response

app = Sanic(__name__)


# webapp path defined used route decorator
@app.route("/")
def run(request):
    return response.text("Hello World !")


# debug logs enabled with debug = True
app.run(host="0.0.0.0", port=8000, debug=True)
