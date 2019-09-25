
from flask import Flask, request
from influxInterface import writeToInflux

app = Flask(__name__)

@app.route('/telemetry', methods=["POST"])
def postTelemetry():
    data = request.data
    try:
        writeToInflux(data)
        return 200
    except Exception as e:
        print(e)
        return 500