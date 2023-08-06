import json
import string
import random  # define the random module
import requests

from Rotic.Models.Response import *


class Request:
    sdk = None
    unique_token = None

    def __init__(self):
        self.sdk = RoticSDKModel()
        self.unique_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

    def MakeRequest(self, token, api, data, unique_token=None):

        try:
            Ai_uri = "https://api.rotic.ir/v2/services/" + token + "/ai"

            if unique_token is None:
                unique_token = self.unique_token

            form = {
                "data": data,
                "token": token,
                "api": api,
                "unique_token": unique_token,
                "driver": "api"
            }

            response = json.loads(requests.post(Ai_uri, data=form).text)

            responseObject = []

            for item in response["response"]:
                rs = Response()
                responseObject.append(rs.object(value=item["value"], value_type=item["type"], images=item["images"],
                                                buttons=item["buttons"]))

            return self.sdk.object(response=responseObject)
        except:
            responseObject = [{
                "value": None,
                "buttons": [],
                "images": None,
                "type": "text",
            }]
            return self.sdk.object(response=responseObject, status=False, code=500, message="An error error happened "
                                                                                            "in request!")
