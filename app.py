from datetime import datetime
from google.cloud import vision
from google.cloud.vision import types
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from json import dumps
from base64 import b64encode, b64decode
from requests import post
from os import environ

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

HEADERS = {
    "x-api-key": environ.get("TRUE_FACE_API_KEY"),
    "Content-Type": "application/json"
}

TRUE_FACE_COLLECTION_ID = "ahBzfmNodWlzcGRldGVjdG9ychcLEgpDb2xsZWN0aW9uGICAgMCB2L8IDA"

sid_to_uid_response = {}

firebase_cred = credentials.Certificate("./secret/firebase-adminsdk.json")
firebase_app = firebase_admin.initialize_app(firebase_cred, {
    'databaseURL': 'https://mehsurvey-29210.firebaseio.com'
})

@app.route('/info', methods=['GET'])
@cross_origin()
def getinfo():
    return jsonify({"version": "0.0.1"})

@app.route('/authenticate', methods=['POST'])
@cross_origin()
def get():
    body = request.get_json()
    image = body['image']
    url = "https://api.chui.ai/v1/identify"
    data = {
        "img": image,
        "collection_id": TRUE_FACE_COLLECTION_ID
    }
    identify_response = post(url, data=dumps(data), headers=HEADERS).json()
    identify_data = identify_response.get("data", None)

    if not identify_data:
        return jsonify({"user_found": "false"})
    else:
        if identify_data["success"] is False:
            return jsonify({"user_found": "false"})

    return jsonify({"user_found": "true"})

@app.route('/register', methods=['POST'])
@cross_origin()
def registerUser():
    body = request.get_json()
    if 'image0' not in body or 'image1' not in body or 'image2' not in body:
        return jsonify({"error": "Missing image parameters (3 is needed)"})
    if 'name' not in body:
        return jsonify({"error": "Missing name parameter"})
    image0 = body['image0']
    image1 = body['image1']
    image2 = body['image2']
    # image3 = body['image3']
    # image4 = body['image4']
    name = body['name']
    url = "https://api.chui.ai/v1/enroll"
    data = {
        "img0": image0,
        "img1": image1,
        "img2": image2,
        # "img3": image3,
        # "img4": image4,
        "name": name,
        "collection_id": TRUE_FACE_COLLECTION_ID
    }
    register_response = post(url, data=dumps(data), headers=HEADERS).json()
    register_success = register_response.get("success", False)

    # if not identify_data:
    #     return jsonify({"user_found": "false"})
    # else:
    #     if identify_data["success"] is False:
    #         return jsonify({"user_found": "false"})

    url = "https://api.chui.ai/v1/train"
    if register_success:
        train_response = post(url, data=dumps({ "collection_id": TRUE_FACE_COLLECTION_ID }), headers=HEADERS).json()
        train_success = train_response.get("success", False)
        if train_success:
            return jsonify({"success": True, "raw_response": train_response})
        else:
            return jsonify({"success": False, "raw_response": train_response})
    else:
        return jsonify({"success": False, "raw_response": register_response})



def decode_base64(data):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += b'='* (4 - missing_padding)
    return b64decode(data)

@app.route("/emotion", methods=['POST'])
@cross_origin()
def get_emotion():
    body = request.get_json()
    image_base64 = body['image']
    client = vision.ImageAnnotatorClient()

    content = decode_base64(image_base64)
    image = types.Image(content=content)

    result = client.face_detection(image=image).face_annotations

    response = {}
    for face in result:
        response['joy'] = face.joy_likelihood
        response['sorrow'] = face.sorrow_likelihood
        response['anger'] = face.anger_likelihood
        response['surprise'] = face.surprise_likelihood
    print response
    return jsonify(response)

# Survey Responses Endpoints

@app.route("/surveys/<survey_id>/responses", methods=['POST'])
@cross_origin()
def saveSurveyResponse(survey_id):
    body = request.get_json()
    user_id = body["user_id"]
    responses = body["responses"]
    responsesRef = db.reference('surveys/' + str(survey_id) + '/responses/' + str(user_id))
    responsesRef.set({
        "survey_id": survey_id,
        "user_id": user_id,
        "responses": responses,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    return jsonify(responsesRef.get())

@app.route("/surveys/<survey_id>/responses", methods=['GET'])
@cross_origin()
def getSurveyResponse(survey_id):
    ref = db.reference('surveys/' + str(survey_id) + '/responses')
    val = ref.get()
    if val is None:
        return jsonify({})
    else:
        return jsonify(ref.get())

@app.route("/surveys/<survey_id>/responses", methods=['DELETE'])
@cross_origin()
def clearSurveyResponse(survey_id):
    ref = db.reference('surveys/' + str(survey_id) + '/responses')
    ref.set({})
    return jsonify({ "success": True })

# Survey CRUD

@app.route("/surveys", methods=['GET'])
@cross_origin()
def getSurveys():
    refs = db.reference('surveys')
    val = refs.get()
    if val is None:
        return jsonify({})
    else:
        return jsonify(refs.get())

@app.route("/surveys/<survey_id>", methods=['GET'])
@cross_origin()
def getSurvey(survey_id):
    ref = db.reference('surveys/' + str(survey_id) + '/survey')
    val = ref.get()
    if val is None:
        return jsonify({})
    else:
        return jsonify(ref.get())

@app.route("/surveys", methods=['POST'])
@cross_origin()
def createSurvey():
    body = request.get_json()
    surveyRefs = db.reference('surveys')
    ref = surveyRefs.push()
    ref.set(body)
    return jsonify(ref.get())

@app.route("/surveys/<survey_id>", methods=['DELETE'])
@cross_origin()
def deleteSurvey(survey_id):
    ref = db.reference('surveys/' + str(survey_id))
    ref.set({})
    return jsonify({ "success": True })

if __name__ == '__main__':
    app.run(port='5002')
