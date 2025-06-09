"""Main program for chat application."""
import asyncio
import argparse
import sys

import gradio as gr
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse,\
     SystemPromptPart, UserPromptPart, TextPart

import agent

def convert_gradio_history_to_pydanic_history(msgs:list[dict[str,str]]) -> list[ModelMessage]:
    """This conversion is needed because Gradio uses a simple list of dicts inspired by OpenAI as its message history format,
    while Pydantic uses its own strongly typed representation. In the conversion, we only care about the
    user requests and agent responses.
    """
    result = []
    for msg in msgs:
        if msg['role']=='user':
            result.append(ModelRequest(parts=[UserPromptPart(msg['content'])]))
        elif msg['role']=='assistant':
            result.append(ModelResponse(parts=[TextPart(msg['content'])]))
        else:
            print(f'Ignoring unexpected message role {msg['role']}, content was {msg['content']}')
    return result



def call_agent(message, chat_history, mcp_server, model, debug):
    if debug:
        print("call_agent")
        print("==========")
        print()
        print(f"Chat history has {len(chat_history)} messages")
    pydantic_history = convert_gradio_history_to_pydanic_history(chat_history)
    result = asyncio.run(agent.call_agent(message, history=pydantic_history, mcp_server=mcp_server, model=model, debug=debug))
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": result})
    return "", chat_history


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=7860, type=int,
                        help="Port for the chat server, defaults to 7860")
    parser.add_argument('--mcp-server', default=agent.DEFAULT_MCP_SERVER,
                        help=f"URL for the MCP server, defaults to '{agent.DEFAULT_MCP_SERVER}'")
    parser.add_argument('--model', default=agent.DEFAULT_MODEL,
                        help=f"Model for the Pydantic agent to use, defaults to '{agent.DEFAULT_MODEL}'")
    parser.add_argument('--debug', action='store_true', default=False,
                        help="If specified, print additional debug information")
    args = parser.parse_args(argv)
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(type="messages")
        msg = gr.Textbox(label="Enter your query here")
        clear = gr.ClearButton([msg, chatbot])
        msg.submit(lambda message, chat_history: call_agent(message, chat_history, mcp_server=args.mcp_server, model=args.model,
                                                            debug=args.debug),
                   [msg, chatbot], [msg, chatbot])
    demo.launch(server_port=args.port)

if __name__ == "__main__":
    main()

