# trueface-ai-hackathon-server
Python Server

## Run locally
Clone the repo and change into that directory.

Run these commands in your terminal:
```sh
export TRUE_FACE_API_KEY={YOUR_API_KEY_HERE}
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials-key.json
pip install virtualenv
virtualenv ./env
source ./env/bin/activate
pip install -r requirements.txt
python app.py
```

## Run on heroku
```sh
heroku git:remote -a <project name>
heroku config:set TRUE_FACE_API_KEY={YOUR_API_KEY_HERE}
heroku config:set GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials-key.json
git push heroku master
```