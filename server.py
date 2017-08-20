from google.cloud import vision
from google.cloud.vision import types
from flask import Flask, request, jsonify
from json import dumps
from base64 import b64encode, b64decode
from requests import post
from os import environ

app = Flask(__name__)

HEADERS = {
    "x-api-key": environ.get("TRUE_FACE_API_KEY"),
    "Content-Type": "application/json"
}

sid_to_uid_response = {}

@app.route('/authenticate', methods=['POST'])
def get():
    image = request.form["image"]
    url = "https://api.chui.ai/v1/match"
    data = {
        "img": image,
        "id": "ahBzfmNodWlzcGRldGVjdG9ychcLEgpFbnJvbGxtZW50GICAgMD-_v0IDA"
    }
    match_response = post(url, data=dumps(data), headers=HEADERS).json()
    match_data = match_response["data"]

    if not match_data:
        return jsonify({"authenticated": "false"})
    else:
        if match_data["emb0_match"] is False:
            return jsonify({"authenticated": "false"})

    return jsonify({"authenticated": "true"})

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
def get_emotion():
    image_base64 = request.form["image"]
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
def store():
    sid = request.form["survey_id"]
    user_id = request.form["user_id"]
    responses = request.form["responses"]
    image = request.form["image"]

    sid_to_uid_response[sid] = {
        user_id: {
            "responses": responses,
            "image": image
        }
    }
    return jsonify({})


@app.route("/fetch", methods=['POST'])
def fetch_by_sid():
    sid = request.form["survey_id"]
    return jsonify(sid_to_uid_response[sid])

if __name__ == '__main__':
    app.run(port='5002')
