from google.cloud import vision
from google.cloud.vision import types
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from json import dumps
from base64 import b64encode, b64decode
from requests import post
from os import environ

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

HEADERS = {
    "x-api-key": environ.get("TRUE_FACE_API_KEY"),
    "Content-Type": "application/json"
}

TRUE_FACE_COLLECTION_ID = "ahBzfmNodWlzcGRldGVjdG9ychcLEgpDb2xsZWN0aW9uGICAgMCB2L8IDA"

sid_to_uid_response = {}

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


@app.route("/store", methods=['POST'])
@cross_origin()
def store():
    body = request.get_json()
    sid = body["survey_id"]
    user_id = body["user_id"]
    responses = body["responses"]
    image = body["image"]

    sid_to_uid_response[sid] = {
        user_id: {
            "responses": responses,
            "image": image
        }
    }
    return jsonify({ "survey_id": sid, "user_id": user_id, "responses": responses })


@app.route("/fetch", methods=['POST'])
@cross_origin()
def fetch_by_sid():
    body = request.get_json()
    sid = body["survey_id"]
    return jsonify(sid_to_uid_response[sid])

if __name__ == '__main__':
    app.run(port='5002')
