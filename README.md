# docker-di-cd-tutorial
Tutorial for docker and CI/CD using Github Actions

📝 *Note* : the commands are given for Linux/MacOS. If you're on Windows and you successfully installed docker, you probably don't need this tutorial because you are strong AF given the pain in the a** that it is.
## 0. Prerequist

- Make sure you have Docker installed  and correctly configured (instructions [here](https://docs.docker.com/get-docker/))
- Python 3 installed (just for startup and app verification before containerization)
- Node 12 installed and npm (for the same reason that above)
- A Heroku account (free subscription don't worry)

## 1. App setup

First we will create a Flask app to expose a simple service, another "Hello World!", because the world is so beautiful! Let's do it !

1. Create a directory and cd inside : `mkdir tutorial && cd tutorial`
2. Do it once again for the app : `mkdir flask && cd flask`
3. Create a virtualenv named venv (to avoid f*cking up your python installation) : `python3 -m venv venv`, and activate it : `source venv/bin/activate`
4. Install Flask package using pip : `pip install Flask`
5. Create a file named `app.py` and copy the code from the Flask documentation to create the base app.

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

- Then we create a directory inside the container named `app` and copy all the files from the current directory to the app directory inside the container.

- Then we use `RUN` to install the dependencies listed in `requirement.txt`

- Finally we add `python` as entrypoint and use it with the argument `app.py` to start the app.

### b. Build the image

First we neef to build the image. It means, in a very simplified way, creating the file system for our future containers to run.
- `docker build -t flask .`

Note: Make sure you are in the `./flask` directory when running the command above, the `.` refers to the current context, Docker will try to find a Dockerfile in it.

Once the image is built, you can visualize it among all the others images you have.
- `docker images` . Run it and you should see at least flask and python:3.7-alpine3.12, as Docker needs it to build flask.

### c. Run the container

You successfully built the image, our app is now ready to run. Use docker run to launch the container.
- `docker run flask`

You can visualize the containers running with the following command :
- `docker ps`

You can see the container id, his name, his status etc ... Copy th id and replace the <container id\> in the following command.
- `docker exec -it <container_id> bash`

Yes, you can access the container running ! Try using `ls` or `cd` to see that when have the files copied from our app. (Also note that we land in the `/app` directory as default because we set `WORKDIR` in the Dockerfile).

Remember our app is running on port 5000 ? Let's reach it using curl or a web broswers (http://localhost:5000).

What bro ? Doesn't work ? You sure ? Actually it was intended 😅

Quick explanation : our app do runs on localhost:5000, you can check the container logs (`docker logs --tail <container_id>`) or reach it from *inside* the container, it will work. But we have to tell Docker to forward the http traffic from *our* localhost:5000 to the port 5000 on the container running. To do it we can use the option -p (for ports)
- `docker run -dp 5000:5000 flask`

📝 *Note* : The first number is the port on the host machine (basically here your computer), and the second one is the port on the container. The -d option (concatenated here with the -p one) means running the conatiner in detatched mode, not linked to the opened shell.

You can try again to reach the app from http://localhost:5000 !
### d. Fine tuning

🛠️ Exercise : find the weight of flask's image.
(Hint : use docker images ...)

Holly cow it's heavy ! Something about 900 Mo, for a poor python file running a Flask app ? Let's change that.

We got 2 major ways to reduce the image weight.

1. The files

When running `ls` on /app inside the container before, have you noticed that the `venv` directory was there ? And this README file too, and even the Dockerfile itself ? The app doesn't need those files, and the dependancies are installed running pip so letting the venv in is a terrible idea (doubles the size of the dependencies because they're present 2 times). 

We got 2 options. 

We can first modify the Dockerfile and copy only the files we need. For us it's a very small app it's easy, but for bigger projects it can take quite a number of lines to do so.

2nd option : Docker let us the possibility to add a `.dockerignore` that works as a `.gitignore`. When Docker will run `COPY .` when building the image, it will not copy the files or directory inside the `.dockerignore` file. You can fill it up with the following code.
```
venv/
README.md
Dockerfile
```

2. The base image

🛠️ Exercise: find the base image of python:3.7, and it's weight. (Hint: docker hub ...)

Yes, it's ubuntu. The whole ubuntu. To run a Flask app. There are a lot of ubuntu features that we don't need. We might be able to find a lighter linux distro to run our app. A very famous one is `alpine`. And guess what, the python registry in docker hub has an image based on alpine !
Change the first line of the docker file to :
- `FROM python:3.7-alpine3.12`
- Rebuild the image with `docker build -t flask .`
- Run `docker images`. flask should weight something like 50 mo. Still a bit huge but for now let's say it's good for us.

### e. Express App

We will now setup an Express App using Node.

1. Create a directory in the base directory and cd inside : `mkdir express && cd express`.
2. Run `npm init` to create a p`package.json` file. Press enter to all the options (or fill the fields if you want actually).
3. Create a `app.js` file and copy the following snipet :
```
const express = require('express');
const http = require('http');

const app = express();

app.get('/', (req, res) => {
  res.send('Hello World!');
});

module.exports = app;
```
4. Create a `index.js` file and copy the following code :
```
const app = require('./app');

const port = process.env.PORT || 8000;

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});
```
5. Install express with `npm install express`.
6. In the `package.json` file, add the following line to the scripts object :
```
"start": "node index.js"
```
7. Run `npm start` to start the app. It should display on the shell : `Example app listening at http://localhost:8000`. You can reach the app from http://localhost:8000

Easy pizzy lemon squizzy !

🛠️ Exercise: guess what, try to containerize the app by yourself ! Some hints : try to reproduce the logic we used for the flask app, which image should I use as a base, how to add the files inside the image, how to manage dependencies and app starting.

Here a Dockerfile that could be used (plenty of options to make it work !)
```
FROM node:alpine3.12

WORKDIR /app

COPY . /app

RUN npm install

ENTRYPOINT [ "node" ]

CMD [ "index.js" ]
```
And here is the content of the `.dockignore` :
```
node_modules/
Dockerfile
```

- Now we can built the image if you didn't do it yet : `docker build -t express .`
- And run it with : `docker run -dp 8000:8000 express`
- You can reach the app from http://localhost:8000

You probably noticed the line in `index.js` :
```
const port = process.env.PORT || 8000;
```
We used this syntax to tell Express to use an environment variable as the port value to run the app. If the env variable `PORT` is undefined then the default value is `8000`.

Docker has multiple ways for us to expose env variables.
- Inside the Dockerfile, you can use : `ENV PORT=4000`
- When running the container, you can add the option `--env PORT=4000` or `--env-file .env` to reference a file containing the variables.
- With docker-compose, but I keep that for the last part.

Each solution is better depending of your use case. For instance, the solution in the Dockerfile sets the value at build time, while with `--env` you can set it when starting the container.

### f. Dev with the volumes

Our apps are simple, but imagine we want to implement some new cool features (you can guess we will do it soon ...). We will modify our code, but in order to see the changes we will have to rebuild the image and restart a new container with the new image. So looooooong ... But don't worry Docker got our back, with what they call volumes, and most specificaly here a binding mount.

A binding mount is simply a binding beetwen some files or directory on the host machine, and those inside the container. So for our dev purspose, what we'd like is to link our dev files on our computer and those copied when creating the image with the `COPY` instruction.

Let's do it with the Flask App.
- Use the option `-v` to indicate to Docker to use a volume : `docker run -v "$(pwd)":/app --env -p 5000:5000 flask`
- The `"$(pwd)` command refers to the current working directory, and `/app` is where the app files are located inside the container.
- Flask is well built and if for instance you add a comment and save the file, the app should reload.

Now the Express App.
- Install nodemon as dev dependencie to enable reloading on changes : `npm install --save-dev nodemon`
- Update Dockerfile to use nodemon in docker run command, so remove the `ENTRYPOINT` and `CMD` lines.
- Update start command in `package.json` with value `nodemon index.js`
- Start the container with : `docker run -p 8000:8000 --env PORT=8000 -v "$(pwd)":/app express`
- Tadaaaa, it should reload on changes !

### g. Connect both apps

I want to start by apologizing for the following part. It's a real pain in the a** but you need to do it at least once by hand so that you will fully appreciate the real power of docker-compose.

We will add a route to calculate the n th term of Fibonacci's sequence. We'll do it in the flask app. You can add this code to `app.py` (before the `if __main ...`): 
```
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
```

It simply takes an argument in the url called number and return an dict with the result.

📝 *Note* : This is the recursive version on Fibonacci terms computation, so the complexity is **HUGE**, feel free to use dynamic programmation paterns to improve the speed !

Now we will try to reach this route from the Express App, to create some sort of a proxy. Basically it's useless from an dev point of view, just implement Fibo calculation inside the Express App, but it's for the tutorial's purpose. In the `app.js` file :

- Add the http package after the first express require :
```
const http = require('http');
```

- We will use a env variable to indicate the Flask App url :
```
const flaskUrl = `http://${process.env.FLASK_SERVICE}`;
```

- Finally we add the route `/proxy` to reach the fibo route on the Flask App :
```
app.get('/proxy', (req, res) => {
  http.get(`${flaskUrl}/fibo/10`, (result) => {
    let data = '';
    result.on('data', (d) => {
      data += d;
    });
    result.on('end', () => {
      res.send(data);
    });
  });
});
```

- The final `app.js` file should look like this :
```
const express = require('express');
const http = require('http');

const app = express();
const flaskUrl = `http://${process.env.FLASK_SERVICE}`;

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.get('/proxy', (req, res) => {
  http.get(`${flaskUrl}/fibo/10`, (result) => {
    let data = '';
    result.on('data', (d) => {
      data += d;
    });
    result.on('end', () => {
      res.send(data);
    });
  });
});

module.exports = app;
```

Do you remember the containers are isolated form one another by Docker ? So to make it simple if we try to reach http://localhost:5000, the Flask App url from the Express App, it won't work. We will create a network and bind our two containers to this network to allow the communication between both apps.

- Create a network using : `docker network create tutorial`
- Start the flask container with a connection to this network:
```
docker run -v "$(pwd)":/app -p 5000:5000 --network tutorial --network-alias flask flask
```
- In another terminal start the express container :
```
docker run -p 8000:8000 --env PORT=8000 --env FLASK_SERVICE=flask:5000 -v "$(pwd)":/app --network tutorial express
```
- Test the connection at http://localhost:8000/proxy

Quick breakdown :
- Both containers are connected to the same network `tutorial` using the option `--network tutorial` in the docker run command.
- The flask container is started using the option `--network-alias flask` so that `flask` will now be referenced for Docker as a host pointing to the flask container. It's the same thing with localhost on your computer. You got a file in /etc named hosts (for Linux Users) and if you run `cat /etc/hosts` you should see the line `127.0.0.1 localhost` which indicates that when you want to reach http://localhost:8000, it means http://127.0.0.1:8000 for your computer (you can test it, click on the second link, you will reach the express app).
- We set for `FLASK_SERVICE` env variable the value : `flask:5000` when starting the express container. As explained above, `flask` is now a knwon host for docker and point to the flask container.

Okay, we've done it, congratulations, have a beer my friend, or whatever drink you enjoy before continuing, you deserve it.

### h. Docker-compose : the power of the gods

Have you seen the size of the lasts docker run command we used ? That's the very last thing you want to be that big ... If only there a was a way to reunite all those container building, network creation, container starting ... And there is !

- Add a file called `docker-compose.yml` in the `tutorial` directory with this content :

```
version: "3.7"
services:
  flask-app:
    image: flask
    build:
      context: ./flask
      dockerfile: Dockerfile
    ports:
      - 5000:5000
    volumes:
      - "./flask:/app"
    command: ["python", "app.py"]
  express-app:
    image: express
    build:
      context: ./express
      dockerfile: Dockerfile
    environment:
      PORT: 8000
      FLASK_SERVICE: flask-app:5000
    ports:
      - 8000:8000
    volumes:
      - "./express:/app"
    command: ["npm", "start"]
```

Let's break it down.
- We start by specifying the compose version to use, here it's `3.7`
- Then comes the services declarations. A service will basicaly be an app in our case, with an given image, ports etc ...
- Our first service is called `flask-app`. We can specify which image the container will be started from.
- Interesting option is the build section. It enables you to tell Docker how to build the container's image before runnning it.
- Then we got the environment section with our env variables, the ports and the volumes with our binding mounts. Basicaly you find everything we had in the lasts docker run commands but declared in a file.
- New thing though is the command section. It tells Docker what command to run at container startup.

You can update both Dockerfiles to remove the last 2 lines that where `ENTRYPOINT` and `CMD`, the applications startup will be handled by the command section from the `docker-compose.yml` file. 

Now lauch it with  `docker-compose up`.

📝 *Note* : You can build the containers before lauching them with the option `--build` (`docker-compose up --build`). Also as docker build looks for `Dockerfile` file, docker-compose will look for a `docker-compose.yml` file in the current context. If our file is not named that way of maybe if we have multiple docker-compose files, we can use the option `-f <file/path>`, referencing the file we want (and this option is also available for docker build).

## 3. Add the CI/CD pipelines

- `pip install flake8 pytest pytest-cov`