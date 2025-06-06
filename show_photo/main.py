import os, sys
from fastmcp import FastMCP, Context

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.auth_provider import AuthTokenAuthProvider


auth_token=os.getenv('AUTH_TOKEN')
mcp = FastMCP(name=__name__, auth=AuthTokenAuthProvider([auth_token]))


def get_profile_id(ctx: Context):
    return ctx.get_http_request().headers.get('M-PROFILE-ID')


@mcp.tool()
def show_photo(
    ctx: Context
) -> dict:
    """Show photo"""
    # profile_id = get_profile_id(ctx)
    # print(profile_id)
    return {"operation": "show_image", "image_url": "https://speaak.s3.us-east-1.amazonaws.com/maya.jpg"}
    

if __name__ == '__main__':
    mcp.run(transport="streamable-http", host="0.0.0.0", port=os.getenv("PORT", 8080))



