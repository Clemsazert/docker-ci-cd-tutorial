from flask import Flask
import os

PORT = int(os.environ.get("PORT", default="5000"))

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


def fibo(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibo(n - 1) + fibo(n - 2)


@app.route('/fibo/<number>')
def fibo_service(number):
    return {"result": fibo(int(number))}


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=PORT)
