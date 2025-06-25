# MCP Server with Mem0 for Managing Memories

This demonstrates a structured approach for using an [MCP](https://modelcontextprotocol.io/introduction) server with [mem0](https://mem0.ai) to manage memories efficiently. The server provides essential tools for storing, retrieving, searching, updating, and deleting any kind of memory (such as code snippets, notes, implementation details, or patterns).

## Installation

1. Clone this repository
2. Initialize the `uv` environment:

```bash
uv venv
```

3. Activate the virtual environment:

```bash
source .venv/bin/activate
```

4. Install the dependencies using `uv`:

```bash
# Install in editable mode from pyproject.toml
uv pip install -e .
```

5. Update `.env` file in the root directory with your mem0 API key:

```bash
MEM0_API_KEY=your_api_key_here
```

## Usage with 11.ai and ngrok

1. Start the MCP server:

```bash
uv run main.py
```

2. Expose your local server to the internet using [ngrok](https://ngrok.com/):

```bash
ngrok http 8080
```

3. Copy the HTTPS forwarding URL provided by ngrok (e.g., `https://xxxx-xx-xx-xx-xxxx.ngrok-free.app`).

4. In 11.ai, configure your agent or integration to connect to the MCP server using the ngrok HTTPS URL, appending `/sse` (e.g., `https://xxxx-xx-xx-xx-xxxx.ngrok-free.app/sse`).

5. Use the tools provided by this server for memory management directly from 11.ai.

## Features

The server provides generic CRUD tools for managing memories:

1. `create_memory`: Store any kind of information, such as code snippets, notes, implementation details, or patterns. Include complete context, metadata, and examples as needed.
2. `read_all_memories`: Retrieve all stored memories to analyze, review, or ensure no relevant information is missed.
3. `search_memories`: Semantically search through stored memories to find relevant information, code, solutions, best practices, setup guides, or documentation.
4. `update_memory`: Update an existing memory entry by its ID with new content.
5. `delete_memory`: Delete a memory entry by its ID to remove outdated or incorrect information.

## Why?

This implementation allows for a persistent memory management system that can be accessed via MCP. The SSE-based server can run as a process that agents connect to, use, and disconnect from whenever needed. This pattern fits well with "cloud-native" use cases where the server and clients can be decoupled processes on different nodes.

### Server

By default, the server runs on 0.0.0.0:8080 but is configurable with command line arguments like:

```
uv run main.py --host <your host> --port <your port>
```

The server exposes an endpoint at `/sse` that MCP clients (such as 11.ai) can connect to for accessing the memory management tools.

