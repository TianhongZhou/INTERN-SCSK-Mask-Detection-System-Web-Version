import json
import requests
import io
from aip import AipBodyAnalysis
from PIL import Image
from io import BytesIO
import base64


# define request sending function
def send_request(method, url, params=None, headers=None):
    method = str.upper(method)

    if method == "POST":
        return requests.post(url=url, data=params, headers=headers)
    elif method == "GET":
        return requests.get(url=url, params=params, headers=headers)
    else:
        return None


def to_image(data_url):
    header, encoded = data_url.split(",", 1)
    data = base64.b64decode(encoded)
    return data


def encode(data_url):
    header, encoded = data_url.split(",", 1)
    im = Image.open(BytesIO(base64.b64decode(encoded)))
    im = im.convert('RGB')
    img_bytes = io.BytesIO()
    im.save(img_bytes, format="JPEG")
    image_bytes = img_bytes.getvalue()
    data = base64.b64encode(image_bytes)
    return data


# function to use SNN API to detect mask
def snn_API_fingMask(base64String):
    method = "POST"
    url = "http://172.17.3.231:81/v2/snn_predict"
    headers = None
    params = {
        "apikey": "1234567890klmnopqrstuvwxyz",
        "file_name": [
            "1.jpg"
        ],
        "img": [
            str(encode(base64String), "utf-8")
        ]
    }

    response = requests.post(url=url, json=params, headers=headers)
    body = response.text
    result = json.loads(body)
    status = result["message"]

    if status == "SUCCESS":
        output = result["resultSet"]["results"][0]["label"]
    else:
        output = "request failed"

    return output, len(result["resultSet"]["results"][0]["label"]), result["resultSet"]["results"][0]["score"]


# function to use baidu API to detect mask
def baidu_API_fingMask(base64string):
    # ID information
    APP_ID = "26474079"
    API_KEY = "fQXQXju5fACi7TBRKcZjuz5n"
    SECRET_KEY = "6oGUZgzqDxil9HTFhIBm3GldR2SlVvjR"
    client = AipBodyAnalysis(APP_ID, API_KEY, SECRET_KEY)
    image = to_image(base64string)

    # using body attribute
    client.bodyAttr(image)
    options = {"type": "face_mask"}

    # using parameter to detect body
    result_http = client.bodyAttr(image, options)
    number_of_people = str(result_http["person_num"])

    if result_http["person_num"] > 0:
        score = str(result_http["person_info"][0]["attributes"]["face_mask"]["score"])

        if result_http["person_info"][0]["attributes"]["face_mask"]["name"] == "戴口罩":
            result = "Wearing mask"
            # result_log = number_of_people + " people, Wearing mask, Confidence score: " + score
        else:
            result = "No mask"
            # result_log = number_of_people + " people, No mask, Confidence score: " + score

    else:
        result = "No human detected"
        # result_log = "No human detected"
        score = "None"

    return result, number_of_people, score
