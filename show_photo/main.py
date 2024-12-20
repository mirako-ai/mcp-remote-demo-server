import os

from flask import Flask, request

app = Flask(__name__)


def check_auth(request):
    if not request.authorization or not request.authorization.token == os.getenv('AUTH_TOKEN'):
        raise PermissionError("Invalid token")


@app.route("/list_tools")
def list_tools():
    check_auth(request)
    return [
        {
            "name": "show-photo",
            "description": "Show photo",
            "parameters": {
                "properties": {
                },
                "required": [],
                "type": "object",
            }
        }
    ]


def message_response(message: str):
    return {
        "status": "success",
        "message": message
    }


def custom_response(message: str, custom: dict):
    response = message_response(message)
    response.update(custom)
    return response


def error_response(error: str):
    return {
        "status": "failed",
        "message": error
    }


@app.route("/call_tool", methods=['POST'])
def call_tool():
    check_auth(request)
    request_json = request.json
    name = request_json["name"]
    arguments = request_json["arguments"]
    profile = request_json["profile"] # profile.id and profile.metis_id will be provided

    if name == "show-photo":
        return custom_response("success", {
            "image_url": ["https://www.google.com/logos/doodles/2021/doodle-champion-island-games-begin-6753651837108462.2-2xa.gif"]
        })
    else:
        return error_response("Invalid tool")



if __name__ == '__main__':
   app.run(port=os.getenv("PORT", 8080))