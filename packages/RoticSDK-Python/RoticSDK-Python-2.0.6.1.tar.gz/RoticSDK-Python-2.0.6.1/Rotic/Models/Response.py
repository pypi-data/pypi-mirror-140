class Response:
    def __init__(self):
        pass

    def object(self, value, buttons=None, images=None, value_type="text"):
        if buttons is None:
            buttons = []
        return {
            "value": value,
            "buttons": buttons,
            "images": images,
            "type": value_type,
        }


class RoticSDKModel:
    def __init__(self):
        pass

    def object(self, response=None, status=True, code=None, message=None, options=None, website="https://rotic.ir",
               source="Rotic Python SDK"):
        if response is None:
            response = []
        if options is None:
            options = []

        return {
            "provider": {
                "website": website,
                "source": source,
            },
            "status": status,
            "response": response,
            "options": options,
            "error": {
                "code": code,
                "message": message,
            }
        }
