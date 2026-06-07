import os
import sys

# Add the parent directory to sys.path so imports work correctly
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from mangum import Mangum

# Import existing logic from basecamp_fastmcp.py
# We import mcp directly
from basecamp_fastmcp import mcp

sse = SseServerTransport("/.netlify/functions/mcp_server/messages")
app = Starlette(debug=True)

@app.route("/sse")
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, mcp.create_initialization_options())

@app.route("/messages", methods=["POST"])
async def handle_messages(request: Request):
    await sse.handle_post_message(request.scope, request.receive, request._send)

# Netlify Functions entry point
handler = Mangum(app, lifespan="off")
