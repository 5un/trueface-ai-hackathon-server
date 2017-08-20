# trueface-ai-hackathon-server
Python Server

Steps to run server locally
Clone the repo and change into that directory.

Run these commands in your terminal:
```sh
export TRUE_FACE_API_KEY={YOUR_API_KEY_HERE}
pip install virtualenv
source env/bin/activate
```

## Run on heroku
```sh
heroku git:remote -a <project name>
heroku config:set TRUE_FACE_API_KEY={YOUR_API_KEY_HERE}
heroku config:set GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials-key.json
git push heroku master
```