from typing import Any, List

from flask import Flask, request

app = Flask(__name__)

@app.route("/list_tools")
def list_tools():
    return [{
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
    }]


def return_response(content: List[Any], isError: bool = False):
    return {
        "isError": isError,
        "content": content,
    }


def return_error_response(error: str, isError: bool = True):
    return {
        "isError": isError,
        "content": [{
            "type": "text",
            "text": error,
        }],
    }

@app.route("/call_tool", methods=['POST'])
def call_tool():
    request_json = request.json
    name = request_json["name"]
    arguments = request_json["arguments"]
    profile = request_json["profile"] # profile.id and profile.metis_id will be provided

    if not arguments:
        raise ValueError("Missing arguments")

    if name == "get-available-lockers-from-zone":
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
            return return_error_response("Invalid zone")
        return return_response([{
            "type": "text",
            "text": text
        }])
    else:
        return return_error_response("Invalid tool")



if __name__ == '__main__':
   app.run()