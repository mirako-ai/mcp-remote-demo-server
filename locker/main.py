import os, sys
from fastmcp import FastMCP, Context
from typing import Annotated
from pydantic import Field
from enum import Enum

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.auth_provider import AuthTokenAuthProvider


auth_token=os.getenv('AUTH_TOKEN')
mcp = FastMCP(name=__name__, auth=AuthTokenAuthProvider([auth_token]))


def get_profile_id(ctx: Context):
    return ctx.get_http_request().headers.get('M-PROFILE-ID')


class Zone(Enum):
    A = "A"
    B = "B"
    C = "C"

@mcp.tool()
def get_available_lockers_from_zone(
    zone: Annotated[Zone, Field(description="Zone code")],
    ctx: Context
) -> str:
    """Get available lockers"""
    # profile_id = get_profile_id(ctx)
    # print(profile_id)
    if zone == Zone.A:
        return "A100"
    elif zone == Zone.B:
        return "[B201,B211]"
    elif zone == Zone.C:
        return "None"
    else:
        raise ValueError("Invalid zone")
    

if __name__ == '__main__':
    mcp.run(transport="streamable-http", port=os.getenv("PORT", 8080))