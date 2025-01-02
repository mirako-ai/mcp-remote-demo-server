# Metis mcp remote tools server demo

This project contains 3 demos:

### 1. locker
* This is a simple demo that offers a tool called `get-available-lockers-from-zone`
, with a parameter `zone` required.
* The result of this demo is hardcoded for simplicity 

### 2. weather
* This is a demo which fetch the weather data from `api.weather.gov`
* There are 2 tools provided `get-alerts` `get-forecast`
* This API only works for querying weather of US locations

### 3. show_photo
* This is a demo that offers a tool called `show-photo` demonstrating an image response
* The result of this demo is hardcoded for simplicity 

## API specifications

In order to be used by Metis, the remote tool server <strong>MUST</strong> follow below specification.

### Authentication
The `authToken` specified in Metis profile will be included in the header of ALL API calls as:
```
Authorization: Bearer [authToken]
```
you may call the `check_auth(request)` method in the samples to verify the authToken in your APIs 

### API 1: list_tools
This API should return a list of tools
* path: `list_tools`
* method: `GET`
* content type: `application/json`
* response: array of tool object
  * tool object properties:
    * `name`
      * the name of your tool, <strong>MUST</strong> be unique within ALL tools (including Metis defaults)
    * `description`
      * a description of your tool, what does your tool do, to let the LLM knows how and when to use your tool
    * `parameters`
      * object, the parameters that your tool needs
      * `type`
        * `object`
      * `properties`
        * object of parameters
          * `title`
            * name of your parameter
          * `type`
            * type, `string`, `number`, etc
          * `description`
            * a description of your parameter
      * `required`
        * array of string, the list of parameters that are mandatory
#### Response Sample
```json
{
    "name": "get-available-lockers-from-zone",
    "description": "Get available lockers",
    "parameters": {
        "properties": {
            "zone": {
                "title": "zone",
                "type": "string",
                "description": "Zone code (valid codes are: A, B, C)"
            }
        },
        "required": ["zone"],
        "type": "object"
    }
}
```

### API 2: `call_tool`
This API will be called to execute a tool
* path: `call_tool`
* method: `POST`
* content type: `application/json`
* request body:
  * `name`
    * tool name to be called
  * `arguments`
    * the parameters object
  * `profile`
    * `id`
      * the profile ID currently calling this tool
    * `metis_id` 
      * the metis ID currently calling this tool
* response:
  * `status`
    * `success` or `fail`
  * `message`
    * the response of the tool
  * `image_url`
    * optional, the url of image to be shown
  * `operation`
    * optional, the custom operation to be executed 
#### Request Sample
```json
{
    "name": "get-available-lockers-from-zone",
    "arguments": { "zone": "B" },
    "profile": { 
      "id": "6d1f66af-f0b0-4630-999d-633df8259372", 
      "metis_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
}
```
#### Response Sample
```json
{
    "status": "success",
    "message": "[B201,B211]"
}
```

## Last step
Specify your url endpoint and authToken at maskott tools field 
```json
[
  {
    "url": "https://your-domain.com[:port]", 
    "authToken": "xxxxxxxxxxxxxxxx"
  }
]
```