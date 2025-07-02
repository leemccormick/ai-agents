from mcp.server.fastmcp import FastMCP
from datetime import date
from datetime import datetime

mcp = FastMCP("current_date_server")

@mcp.tool()
async def get_today() -> date:
    return date.today()

@mcp.tool()
async def get_current_time() -> date:
    return datetime.now()

if __name__ == "__main__":
    mcp.run(transport='stdio')