# docker-ci-cd-tutorial
Tutorial for Docker and CI/CD using Github Actions

📝 *Note* : the commands are given for Linux/MacOS. If you're on Windows and you successfully installed docker, you probably don't need this tutorial because you are strong AF given the pain in the a** that it is.

⚠️ *Warning* : I voluntarily don't deep dive in the core concepts and definitions to keep it simple (like CI/CD, Docker Engine etc ...). At first it was a simple tutorial made for one of roommate who told me "Dude Docker is a nightmare". The purpose was just to understand enough what you do not to execute command like a freaking donkey and mess up everything.

### Table of contents
0. [Prerequist](#prerequist)
1. [App setup](#app-setup)
2. [Containerization](#containerization)
3. [Add the CI/CD pipelines](#cicd-pipelines)

## 0. Prerequist <a name="prerequist"></a>

- Make sure you have Docker installed  and correctly configured (instructions [here](https://docs.docker.com/get-docker/))
- Python 3 installed (just for startup and app verification before containerization)
- Node 12 installed and npm (for the same reason that above)
- Git
- A Github account
- A Heroku account (free subscription don't worry)

## 1. App setup <a name="app-setup"></a>

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

## 2. Containerization <a name="containerization></a>

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

You can update express app's Dockerfile to remove the last 2 lines that where `ENTRYPOINT` and `CMD`, the application startup will be handled by the command section from the `docker-compose.yml` file. 

Now lauch it with  `docker-compose up`.

📝 *Note* : You can build the containers before lauching them with the option `--build` (`docker-compose up --build`). Also as docker build looks for `Dockerfile` file, docker-compose will look for a `docker-compose.yml` file in the current context. If our file is not named that way of maybe if we have multiple docker-compose files, we can use the option `-f <file/path>`, referencing the file we want (and this option is also available for docker build).

## 3. Add the CI/CD pipelines <a name="cicd-pipelines"></a>

### a. Initial blabla

CI/CD is way more than just buzzword used everywhere on various LinkedIn posts and medium articles (as well as agile, AI and Machine Learning, but that's an other story). 

CI means "Continuous Integration". A simple definition would be the fact of updating your code base as often as possible with the new code you produced, while keeping a decent code quality. 

CD, for "Continuous Delevery", means to deliver new versions of your services as often as possible, the best would be almost real time when you finish developping a new feature.

For both CI and CD, one main motivation is automation. If you already deployed by hand a website or a backend you know it could be really annoying (to be polite). Because the less time you spend deploying, the more time you have to build new features (to make more [moulaga](https://www.youtube.com/watch?v=5OAysfkcMjg) !). For CI it's more about making sure you didn't break something or what you developped actually works as intended (the sooner you detect an issue, the easier it is to fix).

Done with the talking, let's go now.

### b. Versionning of the project

If it's not done yet, you can use git in your project. We could use 2 repos one for each app. But for pedagogic purpose (and also because it's easier), I suggest to create only one repository.

- cd inside the `tutorial` directory
- Run `git init` to initiate a git repository.
- Create a `.gitignore` with the following content : 
```
# Virtualenv and Caches
*/venv/
*/__pycache__

# Dependencies
*/node_modules/
```

You wouldn't commit the node_modules don't you ? 👿

- Log in to Github and create a new repo.
- Follow Github's instructions to add an existing repository (add the remote and push the existing history)

### c. CI for the Flask App

For he CI part we will focus on 2 aspects : code quality and testing. For that we will use a linter to ensure a decent coding style is respected among our code file, and a test suite to make sure our app is working, with a coverage report in order to see the proportion of code we actually test in our test suite.

- In the flask directory, reactivate your venv : `source venv/bin/activate`
- Install the holy trinity of python package : `pip install flake8 pytest pytest-cov`. Flake8 is a linter, pytest and pytest-cov will help us test our code.
- Create a file `test_suite.py` with the following content :
```
from app import fibo, app

tester = app.test_client()


def test_healthcheck():
    response = tester.get('/', content_type='html/text')
    assert(response.status_code == 200)
    assert(response.data == b'Hello, World!')


def test_fibo_route():
    response = tester.get('/fibo/10', content_type='html/text')
    assert(response.status_code == 200)
    assert(response.data == b'{"result":55}\n')
```

⚠️ *Warning* : yes it's not the best tests in the world, but it's not the purpose of this tutorial, there are plenty of articles on how to wright tests suites all over the web !

We simply test the response of the 2 routes we have using app test_client provided by Flask.

- Run the tests with `pytest -v --cov=app`, you should have a coverage of about 90%, great success !

- Run `flake8 --exclude venv --statistics`. Modify the files according to the errors reported by flake8.

### d. A worklow for the Flask App

We will use Github Actions to manage our CI/CD pipelines.

- Create a `.github` directory in the root of the project, with a `workflows` directory in it.
- Inside create a file named `flask-workflow.yml`.
- First we need to manage the triggers aka when the workflow will run. We want it to run at every push on the branch master (or main depending on your repo). Add the following snipet to `flask-workflow.yml` :
```
name: Flask CI/CD

on:
  push:
    branches: [main]
```
- Now we need to define jobs. The first one will be the ci.
```
jobs:
  ci-flask:
```
- Github wants know on which plateform to run the jobs. For us it will be a container with the latest ubuntu version.
```
jobs:
  ci-flask:
    runs-on: ubuntu-latest
```
- We continue with the steps, meaning the operations we want to perform during the workflow.
```
jobs:
  ci-flask:
    runs-on: ubuntu-latest
    steps:
```
- First step : we use a Github Action to enable the CI to access our repository. A Github Action is just a ready to use step of workflow made by the community. You can search for them in the Github Market Place. Like always the idea is not to reinvent the wheel.
```
jobs:
  ci-flask:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
```
- Now we need to setup Python. And guess what ? There also an action for that. Just make sure to select the right python version you used for the projet (3.7 like the image we used)
```
steps:
  - uses: actions/checkout@v2
  - name: Setup Python
    uses: actions/setup-python@v2
    with:
      python-version: 3.7
      architecture: x64
```
- Like we did with the Dockerfile, we need to install the dependencies.
```
steps:
  - uses: actions/checkout@v2
  - name: Setup Python
    uses: actions/setup-python@v2
    with:
      python-version: 3.8.5
      architecture: x64
  - name: dependencies
    run: pip install -r requirement.txt
    working-directory: ./flask
```
The structure of the step is always the same : you can just run a command with `run`, you can give a name to your step with `name`. For the actions you must use `uses`, and sometimes they have options or need parameters you give can them with tag `with`.
- Now we are ready to add our own commands. First the linter :
```
- name: linter
  run: flake8 --statistics
  working-directory: ./flask
```
The `working-directory` option is usefull for us as we have a single repo with 2 apps inside, so that we can specify where to run the steps.

- Then we add the test command.
```
- name: test
  run: pytest -v --cov=app
  working-directory: ./flask
```
- And we are done for our first job. Commit and push it, you should see the workflow running in the Action section of your repository.

### e. Deploying the app and setup the CD

We will use Heroku to deploy our 2 services, since it has a container registry system and a container runtime option.

- Log in to Heroku and create a new app.
- Come back to our `flask-workflow.yml` file. Let's define an other job called deploy-flask. By default, jobs of a same workflow runs in parallel, but we don't want to deploy our app if the linter found coding style issues or if the tests failed. For that we use the `need` option to ensure the first job as succeed before running the second one.
```
deploy-flask:
    needs: ci-flask
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
```
- We will need only one real step. There is a cool action built to Deploy on Heroku with Docker, be sure to [check out](https://github.com/marketplace/actions/deploy-to-heroku) and star it.
```
- uses: akhileshns/heroku-deploy@v3.8.9
  with:
    heroku_api_key: ${{secrets.HEROKU_API_KEY}}
    heroku_app_name: ${{secrets.HEROKU_FLASK_APP_NAME}}
    heroku_email: ${{secrets.HEROKU_EMAIL}}
    usedocker: true
    appdir: ./flask
```
You have to provide the action your api_key, your email and the app_name. But the Heroku api_key is a very sensitive data, not meant to be share publicly. We have to store it as a secret of our repository, that is also accessible inside the workflows using the syntax `${{secrets.<YOUR_ENV_VAR_NAME>}}`
- Access the repository secrets from `Settings -> Secrets -> New repository secret`
- Create one secret for each variable (I've also added email and app name even though it's not very sensitive)
- Commit and push your changes, after the workflow is completed you should be able to see in the Heroku app activity a deployment.

Reach your app on Heroku (Open App button). What do you mean it doesn't work ? Actually it was intended once again. You remember the networking setup, the option to forward port to the container etc ... ?

Actually what Heroku does is exposing to your container an env variable called `PORT` **that you cannot override** and forward all traffic from port 80 (basic http) of your app toward this port.

We need to tell Flaks to run the app using this port. Don't be afraid it's not a big deal.

- In `app.py` after the first line append the following code to get the env variable :
```
import os

PORT = int(os.environ.get("PORT", default="5000"))
```

- Replace the last lines with :
```
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=PORT)
```

- Commit and push your changes. If the workflow doesn't fail, you should see an other deployment of your app and should be able to access it.
