# RoticSDK-Python
Python SDK let you call Rotic Intelligent Solutions API

For Chat:

```angular2html
rotic = RoticSDK()
rotic.token = "{YOUR_TOKEN}"
rotic.api = "{YOUR_API_TOKEN}"
rotic.unique_token="{Random_Generated_String}"
print(rotic.chat("Hello world"))
```