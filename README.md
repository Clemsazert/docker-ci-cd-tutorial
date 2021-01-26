# docker-di-cd-tutorial
Tutorial for docker and CI/CD using Github Actions

Note : the commands are given for Linux/MacOS. If you're on Windows and you successfully installed docker, you probably don't need this tutorial because you are strong AF given the cancer that it is.
## 0. Prerequist

- Make sure you have docker installed  and correclty configured (instructions [here](https://docs.docker.com/get-docker/))
- Python 3 installed (just for startup and app verification before containerization)

## 1. App setup

First we will create a Flask app to expose a simple service, annother "Hello World!" because the world is so beautiful! Let's do it !

1. Create a directory and cd inside : `mkdir myapp && cd myapp`
2. Create a virtualenv named venv (to avoid f*cking up your python installation) : `python3 -m venv venv`, and activate it : `source venv/bin/activate`
3. Install Flask package using pip : `pip install Flask`
4. Create a file named `app.py` and copy the code from the Flask documentation to create the base app.

```
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
```
5. Run `python app.py` and you should see the server starting up. You can reach it on http://localhost:5000. It should respond "Hello World!".

## 2. Containerization

### a. Dockerfile

We will create the Dockerfile to build the image of a container with our app within.

- Create a file named `Dockerfile` and copy the code bellow.

```
FROM python:3.7

WORKDIR /app

COPY . /app

RUN pip install -r requirement.txt

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]
```

- We use the official python 3.7 image available on [dockerhub](https://hub.docker.com/_/python) with line `FROM python 3.7`

- We then create a directory inside the container named `app` and copy all the files from the current directory to the app directory inside the container.

- Then we use `RUN` to install the dependencies listed in `requirement.txt`

- Finally we add `python` as entrypoint and use it with the argument `app.py` to start the app.

### b. Build the image

- `docker build -t myapp .`
- `docker images`

### c. Run the container

- `docker run myapp`
- `docker ps`
- `docker exec -it <container_id> bash`
- `docker run -dp 5000:5000 myapp`

### d. Fine tuning

- Add .dockerignore
```
venv/
README.md
.gitignore
```
- `FROM python:3.7-alpine3.12`
- Rebuild

### e. Express App

- 
## 3. Add the CI

- `pip install flake8 pytest pytest-cov`