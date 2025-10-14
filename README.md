# Mirako mcp remote tools server demo

This project contains 3 demos:

### 1. locker
* This is a simple demo that offers a tool called `get_available_lockers_from_zone`
, with a parameter `zone` required.
* The result of this demo is hardcoded for simplicity 

### 2. weather
* This is a demo which fetch the weather data from `api.weather.gov`
* There are 2 tools provided `get_alerts` `get_forecast`
* This API only works for querying weather of US locations

### 3. show_photo
* This is a demo that offers a tool called `show_photo` demonstrating an image response
* The result of this demo is hardcoded for simplicity 

## Authentication
The `auth_token` specified in profile will be included in the header of ALL API calls as:
```
Authorization: Bearer [auth_token]
```
you may use the `AuthTokenAuthProvider` class from [`auth/auth_provider.py`](auth/auth_provider.py) as your AuthProvider like this:
```
from auth.auth_provider import AuthTokenAuthProvider

mcp = FastMCP(name=__name__, auth=AuthTokenAuthProvider([auth_token]))
```

## Profile ID
profile ID will be included in the header, you may call the `get_profile_id(ctx)` method in the samples to get the profile ID if needed

## Supported transport options
`streamable-http`

## Supported MCP Components
[`Tool`](https://gofastmcp.com/servers/tools#tools)
```
@mcp.tool()
def addition(
    a: Annotated[int, Field(description="first number to be added")],
    b: Annotated[int, Field(description="second number to be added")],
    ctx: Context
) -> dict:
    """Add 2 numbers"""
    # profile_id = get_profile_id(ctx)
    return a+b
```

## Return type
Supported return types:
* str
  * return the response directly as str for text responses

### Operation
Return a dict for operations, the operation name should be specified in `operation` key

#### Show Image
You should return an publicly accessible URL in `image_url` in order to show an image, format as below:
```
return {"operation": "show_image", "image_url": "https://your-domain.com/image.jpg"}
```

## How to setup your tool in profile
You may setup multiple MCP tool servers in a profile
```
[
  {
    "url":"http://localhost:8080/mcp/",
    "auth_token":"abc"
  },
  {
    "url":"http://localhost:8081/mcp/",
    "auth_token":"abcd"
  }
]
```
| Parameter | Type | Required | Description |
| -------- | ------- | ------- | ------- |
| url | str | true | the enpoint URL |
| auth_token | str | if `api_key` is not provided | Auth Token, will be passed in `Authorization` header with the “Bearer” scheme |
| api_key | str | if `auth_token` is not provided | API Key, will be passed in `X-API-KEY` header |

## Testing
You may use `tester/main.py` to test your MCP server. Change the `URL`, `Auth Token` and `profile ID` here if needed.
```
transport = StreamableHttpTransport(
    "http://localhost:8080/mcp/",
    auth=BearerAuth("your auth token"),
    headers={"M-PROFILE-ID": "your profile ID"},
)
```

### Run tester
```
python tester.main.py
```

## CloudRun Sample
Refer to [`cloudrun-sample/README.md`](cloudrun-sample/README.md)