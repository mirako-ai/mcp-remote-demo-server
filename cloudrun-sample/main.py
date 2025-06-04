import functions_framework
import os

headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
}

def check_auth(request):
    if not request.authorization or not request.authorization.token == os.getenv('AUTH_TOKEN'):
        raise PermissionError("Invalid token")


def list_tools(request):
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
        },
        {
            "name": "get-available-lockers-from-zone",
            "description": "Get available lockers",
            "parameters": {
                "properties": {
                    "zone": {
                        "title": "zone",
                        "type": "string",
                        "description": "Zone code (valid codes are: A, B, C)"
                    },
                },
                "required": ["zone"],
                "type": "object",
            },
        }
    ]


def message_response(message: str):
    return ({
        "status": "success",
        "message": message
    }, 200, headers)


def custom_response(message: str, custom: dict):
    json = {
        "status": "success",
        "message": message,
    }
    json.update(custom)

    return (json, 200, headers)


def error_response(error: str):
    return ({
        "status": "failed",
        "message": error
    }, 200, headers)


def call_tool(request):
    check_auth(request)
    request_json = request.get_json(silent=True)
    name = request_json["name"]
    arguments = request_json["arguments"]
    profile = request_json["profile"] # profile.id and profile.metis_id will be provided

    if name == "show-photo":
        return custom_response("success", {
            "image_url": "https://speaak.s3.us-east-1.amazonaws.com/maya.jpg"
        })
    elif name == "get-available-lockers-from-zone":
        if not arguments:
            raise ValueError("Missing arguments")

        zone = arguments.get("zone")
        if not zone:
            raise ValueError("Missing zone parameter")

        if zone == "A":
            text = "A100"
        elif zone == "B":
            text = "[B201,B211]"
        elif zone == "C":
            text = "None"
        else:
            return error_response("Invalid zone")
        return message_response(text)
    else:
        return error_response("Invalid tool")



@functions_framework.http
def main_handle(request):
    path = request.path
    method = request.method

    if path == "/list_tools" and method == "GET":
        return list_tools(request)
    elif path == "/call_tool" and method == "POST":
        return call_tool(request)

    return error_response("Invalid request")