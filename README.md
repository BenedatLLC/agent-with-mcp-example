# Agent with MCP Example

This project provides a simple example of an Agent and a local MCP server.

The MCP Server provides a collection of tools for obtaining system CPU and memory statistics.
It is built on the [psutil](https://psutil.readthedocs.io/en/latest/#) library. The tools are implemented
as FastAPI enpoints and then exposed via MCP using [fastapi-mcp](https://github.com/tadata-org/fastapi_mcp).

The Agent is part of a simple Gradio chat application. The agent uses the Pydantic.ai
[agent framework](https://ai.pydantic.dev). The agent is provided the MCP Server's
URL and a system prompt indicating that it should answer system resource usage. The Gradio
Chat component maintains a conversation history so that you can ask follow-up questions.

## Setup

### Prerequisites
First make sure you have the following tools installed on your machine:
1. [uv](https://docs.astral.sh/uv/), a package and environment manager for Python
2. [direnv](https://direnv.net), a tool for managing environment variables in your projects
3. [mcptools](https://github.com/f/mcptools) (optional), a command line utility for interacting
   with MCP servers
4. These examples use OpenAI models for the Agent, so you will need an actve account and key
   from [here](https://platform.openai.com/api-keys).  Alternatively, you can use one of the
   other models supported by Pydantic.ai. In that case, you will have to set the model and key
   appropriately.

### Setup steps
Once you have the prerequisites installed, do the following steps:
1. Copy envrc.template to .envrc and edit the value of OPENAI_API_KEY to your Open AI token.
2. Run `direnv allow` to put the changed environment variables into your environment.
3. Run `uv sync` to create/update your virtual environment.
4. You can start the MCP Server with `uv run psutil_mcp.py`. By default it will server on port 8000.

### Testing
If you have installed mcptools, you can connect to your MCP server and test it as follows:

```sh
$ mcpt shell http://localhost:8000/mcp
mcp> tools
cpu_times
     Get Cpu Times Return system CPU time as a total across all cpus. Every attribute represents the
...

mcp> call cpu_times
{
  "user": 119528.44,
  "nice": 0.0,
  "system": 67114.2,
  "idle": 2692773.55
}
mcp> exit
```
## Running
To run the full application:
1. If you have not already stared your MCP Server, you can run it as `uv run psutil_mcp.py`
2. In another terminal window, start the chat server with `uv run chat.py`
3. Point your browser to http://127.0.0.1:7860

## Extras
The psutil_mcp.py and chat.py programs have some command line options to enable debugging, change the
model, change the ports, etc. Run them with the `--help` option to see the available options.

There is a configuration for VSCode to use the MCP server at `.vscode/mcp.json`