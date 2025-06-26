from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
from mem0 import MemoryClient
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize FastMCP server for mem0 tools
mcp = FastMCP("mem0-mcp")

# Initialize mem0 client and set default user
mem0_client = MemoryClient()
DEFAULT_USER_ID = "chrome-extension-user"
CUSTOM_INSTRUCTIONS = """
Extract the Following Information:  

- Code Snippets: Save the actual code for future reference.  
- Explanation: Document a clear description of what the code does and how it works.
- Related Technical Details: Include information about the programming language, dependencies, and system specifications.  
- Key Features: Highlight the main functionalities and important aspects of the snippet.
"""
mem0_client.update_project(custom_instructions=CUSTOM_INSTRUCTIONS)

@mcp.tool(
    description="""Create a new memory entry in mem0. This tool stores any kind of information, such as code snippets, notes, implementation details, or patterns for future reference. When storing a memory, you should include:
    - Complete context and all necessary details
    - Any relevant metadata (e.g., language, version, tags)
    - Example usage or scenarios
    - Known limitations or considerations
    The memory will be indexed for semantic search and can be retrieved later using natural language queries."""
)
async def create_memory(text: str) -> str:
    """Create a new memory entry in mem0.

    Args:
        text: The content to store in memory, including any context, code, or documentation
    """
    try:
        messages = [{"role": "user", "content": text}]
        mem0_client.add(messages, user_id=DEFAULT_USER_ID, output_format="v1.1")
        return f"Successfully added memory: {text}"
    except Exception as e:
        return f"Error adding memory: {str(e)}"

@mcp.tool(
    description="""Retrieve all stored memories for the default user. Call this tool when you need complete context of all previously stored information. This is useful when:
    - You need to analyze all available notes or patterns
    - You want to check all stored examples or solutions
    - You need to review the full history of stored information
    - You want to ensure no relevant information is missed
    Returns a comprehensive list of all memories in JSON format with metadata."""
)
async def read_all_memories() -> str:
    """Get all memories for the default user.

    Returns a JSON formatted list of all stored memories, including:
    - Content and patterns
    - Documentation
    - Best practices
    - Setup guides and examples
    Each memory includes metadata about when it was created and its content type.
    """
    try:
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID, page=1, page_size=50)
        flattened_memories = [memory["memory"] for memory in memories["results"]]
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error getting memories: {str(e)}"

@mcp.tool(
    description="""Search through stored memories using semantic search. This tool should be called for EVERY user query to find relevant information, code, or implementation details. It helps find:
    - Specific implementations or patterns
    - Solutions to problems
    - Best practices and standards
    - Setup and configuration guides
    - Documentation and examples
    The search uses natural language understanding to find relevant matches, so you can describe what you're looking for in plain English. Always search the memories before providing answers to ensure you leverage existing knowledge."""
)
async def search_memories(query: str) -> str:
    """Search memories using semantic search.

    Args:
        query: Search query string describing what you're looking for. Can be natural language or specific technical terms.
    """
    try:
        memories = mem0_client.search(query, user_id=DEFAULT_USER_ID, output_format="v1.1")
        flattened_memories = [memory["memory"] for memory in memories["results"]]
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error searching memories: {str(e)}"

@mcp.tool(
    description="""Update an existing memory entry. Provide the memory ID and the new content. Useful for correcting or expanding previously stored information."""
)
async def update_memory(memory_id: str, new_text: str) -> str:
    """Update an existing memory entry.

    Args:
        memory_id: The ID of the memory to update.
        new_text: The new content for the memory.
    """
    try:
        mem0_client.update(memory_id=memory_id, data= new_text)
        return f"Successfully updated memory {memory_id}"
    except Exception as e:
        return f"Error updating memory: {str(e)}"

@mcp.tool(
    description="""Delete a memory entry by its ID. Useful for removing outdated or incorrect information."""
)
async def delete_memory(memory_id: str) -> str:
    """Delete a memory entry by its ID.

    Args:
        memory_id: The ID of the memory to delete.
    """
    try:
        mem0_client.delete(memory_id=memory_id)
        return f"Successfully deleted memory {memory_id}"
    except Exception as e:
        return f"Error deleting memory: {str(e)}"

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )
        return Response()

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    import argparse

    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)
