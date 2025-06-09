"""Code for our agent. The agent is written using pydantic.ai agent framework
and uses the tools from our mcp server to answer questions.
If you use the default model (openai:gpt-4o), the environment variable OPENAI_API_KEY
must be set to your key. For other models consult the pydantic.ai documentation.
"""
import asyncio
import sys
from typing import Optional
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP
from pydantic_ai.messages import ModelMessage

from pydantic_utils import pp_run_result

SYSTEM_PROMPT=\
"""You are an expert in the user's computer. Answer questions about their computer's
resource usage using the provided tools.

When asked for a metric "per cpu" be sure to use the appropriate tool
to get a list of values for each cpu and format them in the answer as a list.
Those tools have names ending with _per_cpu.
"""

DEFAULT_MCP_SERVER='http://localhost:8000/mcp'
DEFAULT_MODEL='openai:gpt-4o'

async def call_agent(query:str, mcp_server:str=DEFAULT_MCP_SERVER,
                     history:Optional[list[ModelMessage]]=None, model:str=DEFAULT_MODEL, debug:bool=False) -> str:
    server = MCPServerHTTP(url=mcp_server)
    agent = Agent(model, system_prompt=SYSTEM_PROMPT, mcp_servers=[server])  
    async with agent.run_mcp_servers():
        if debug:
            print("Found the following tools:")
            tools = await server.list_tools()
            for tool in tools:
                print(f"  {tool.name}")
        result = await agent.run(query, message_history=history)
    if debug:
        pp_run_result(result)
    return result.output


if __name__=="__main__":
    print(asyncio.run(call_agent('what is my current cpu utilization?')))