from tools_files import read_permanent_agent_memory, write_permanent_agent_memory
from tools_notes import read_context_note, read_by_zk_note_name, find_relevant_notes_by_zk_note_name, \
    simple_search_note, get_notes_by_level, read_personal_index_note, save_to_notes_storage
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools import DuckDuckGoSearchRun, BraveSearch, WikipediaQueryRun
from langchain_community.tools import FileSearchTool, ReadFileTool, HumanInputRun
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import asyncio

from reminders import add_reminder

mcp_client = MultiServerMCPClient(
    {
        "r-notes-stdio": {
            "command": "uv",
            # Make sure to update to the full absolute path to your mcp_server.py file
            "args": [
                "--directory",
                "./",
                "run",
                "mcp_server.py"
            ],
            "transport": "stdio",
        }
        # "r-notes-http": {
        #     # make sure you start mcp server on port 8000 using `uv run mcp_server.py`
        #     "url": "http://localhost:8000/mcp/",
        #     "transport": "streamable_http",
        # }
    }
)


async def main():
    load_dotenv()

    ## main logic
    model = ChatOllama(
        model="qwen3:30b-a3b-q8_0",
        temperature=0.05,  # lower than recommended default 0.6
    )
    # search = DuckDuckGoSearchRun()
    memory = MemorySaver()
    mcp_tools = await mcp_client.get_tools()
    tools = [
        # read_context_note, read_personal_index_note,
        # get_notes_by_level,
        # read_by_zk_note_name, find_relevant_notes_by_zk_note_name, simple_search_note,
        # add_reminder,
        # read_permanent_agent_memory, write_permanent_agent_memory, save_to_notes_storage,
        # internet tools start here
        # WikipediaQueryRun
        # HumanInputRun,
        *mcp_tools
    ]

    system_message = SystemMessage(
        content="You are helpful assistant to work with personal notes in zettelkasten markdown files. " \
                "CALL TOOL 'read_permanent_memory' in the beginning to refresh your permanent memory." \
                "Before you answer, assess the uncertainty of your response. If it's greater than 0.1, ask me clarifying questions until the uncertainty is 0.1 or lower." \
                "Be succinct in thinking process.")

    agent_executor = create_react_agent(model, tools, prompt=system_message, checkpointer=memory)
    config = {"configurable": {"thread_id": "some thread id", "recursion_limit": 42}}

    while True:
        print("-" * 32)
        user_message = input("\n>> ")
        input_to_model = {"messages": [HumanMessage(content=f"{user_message}")]}
        ## direct invoke
        # response = agent_executor.invoke(input_to_model, config=config)
        # response_messages = response["messages"]
        # for message in response_messages:
        #     message.pretty_print()

        ## streaming
        async for step in agent_executor.astream(
                input_to_model,
                config,
                stream_mode="values",
        ):
            last_message = step["messages"][-1]
            if last_message.type == "ai":
                last_message.pretty_print()

    ## template example
    # template_prompt = ChatPromptTemplate.from_messages([
    #     ("system", "You are a world-class comedian."),
    #     ("human", "Tell me a joke about {topic}")
    # ])
    #
    # str_chain = template_prompt | chat_model | StrOutputParser()
    #
    # # output: AIMessage(content
    # output = chat_model.invoke([
    #     HumanMessage("Tell me a joke about cats!")
    # ])
    # # print(output.tool_calls)
    # print(joke_prompt.invoke({"topic": "test"}))


if __name__ == '__main__':
    asyncio.run(main())


def print_in_color(text: str) -> None:
    # 32 == green
    # 34 == blue
    print(f"\033[34m{text}\033[0m")
