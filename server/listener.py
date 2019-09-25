
import json
from flask import Flask, request, Response
from influxInterface import writeToInflux

app = Flask(__name__)

@app.route('/telemetry', methods=["POST"])
def postTelemetry():
    data = request.data
    try:
        writeToInflux(data)
        return Response({"written": True}, status=200)
    except Exception as e:
        print(e)
        return Response({"error": str(e)}, status=500)


port = 13768
with open('./config.json') as config:
    value = json.loads(config.read())
    port = value["server_port"]

app.run(host="0.0.0.0", port=port)