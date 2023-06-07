# Smart-Pot
A smart pot project carried out as part of a course at the Poznan University of Technology. The project will consist of four parts: ESP8266, API, Mobile App, Web Application and database. Docker will be used to containerise the whole application.

![Untitled-2023-04-03-2212](https://user-images.githubusercontent.com/65020389/229622923-23ce3feb-2568-4b60-8418-3da8456cae97.png)

# Smart Pot API
A smart pot api is a part of smart pot project which get data from ESP8266 about plant information. Also provides functionality about user like registration login etc. Some of endpoint have a authorization for example to get information about user plants.

## Getting started
 1. Clone the repository from GitHub (using HTPS):\
	`git clone https://github.com/Maksymilian-Plywaczyk/Smart-Pot.git`
 2. Create a virtual environment to isolate our package dependencies locally\
	 `python -m venv venv`\
	 `source venv/bin/activate` or on Windows `venv/Scripts/activate`
 3. Install list of dependencies from `requirements.txt`\
	`pip install -r requirements.txt`
 4. Create `.env` file using command: `cp .env.template .env`  and swap `SECRET KEY` with yours [Getting secret key](#getting-secret-key).
5. Run the project using [Docker configuration](#docker-configuration) and you should see the docs in url [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
6. Feel free to use this API :)

## Docker configuration
In order to run the project in a docker container you must run a `docker daemon` on your computer and then type command:
<br/>
`docker compose up --build`
<br/>
There are one container at this moment:
 -   Backend on port 8000 (name: `api`)

Container is configurated to work as development environment so every change in api will trigger auto reload container. 

## GETTING SECRET KEY
To get secret key, which you need to pass in `.env` file you need to type in terminal that command and then copy this to `.env` file:
<br/>
`openssl rand -hex 32`

## Interactive API document
![docs_api](https://github.com/Maksymilian-Plywaczyk/Smart-Pot/assets/65869609/c43d90d6-817c-4580-bf3d-3380c5fb7274)

