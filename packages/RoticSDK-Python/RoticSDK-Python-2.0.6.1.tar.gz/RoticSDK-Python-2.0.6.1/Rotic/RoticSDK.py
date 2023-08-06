from Rotic.Request import Request
from Rotic.Models.Response import *


class RoticSDK:
    token = None
    api = None
    sdk = None
    unique_token = None

    def __init__(self):
        self.sdk = RoticSDKModel()

    def chat(self, data, unique_token=None):
        try:
            if unique_token is None:
                unique_token = self.unique_token

            if self.token is not None and self.api is not None:
                request = Request()
                return request.MakeRequest(token=self.token, api=self.api, unique_token=unique_token, data=data)
            else:
                responseObject = [{
                    "value": None,
                    "buttons": [],
                    "images": None,
                    "type": "text",
                }]
                return self.sdk.object(response=responseObject, status=False, code=207,
                                       message="Token or Api token did not provided!")
        except:
            responseObject = [{
                "value": None,
                "buttons": [],
                "images": None,
                "type": "text",
            }]
            return self.sdk.object(response=responseObject, status=False, code=500, message="An error error happened "
                                                                                            "in connection!")
