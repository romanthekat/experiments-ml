from notes import read_context_note, read_by_zk_note_name, find_relevant_notes_by_zk_note_name, \
    simple_search_note, get_notes_by_level
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools import DuckDuckGoSearchRun


def print_in_color(text: str) -> None:
    # 32 == green
    # 34 == blue
    print(f"\033[34m{text}\033[0m")


def main():
    ## main logic
    model = ChatOllama(
        model="qwen3:30b-a3b",
        temperature=0.6,
    )
    # search = DuckDuckGoSearchRun()
    memory = MemorySaver()
    tools = [read_context_note, read_by_zk_note_name, find_relevant_notes_by_zk_note_name, simple_search_note,
             get_notes_by_level]

    agent_executor = create_react_agent(model, tools, checkpointer=memory)
    config = {"configurable": {"thread_id": "some thread id"}}

    while True:
        user_message = input("\n>> ")
        if user_message == "":
            break

        input_to_model = {"messages": [
            SystemMessage(
                content="You are helpful assistant to work with personal notes in zettelkasten format within markdown files. Be succinct in thinking process."),
            HumanMessage(content=f"{user_message}")]}

        ## direct invoke
        # response = agent_executor.invoke(input_to_model, config=config)
        # response_messages = response["messages"]
        # for message in response_messages:
        #     message.pretty_print()

        ## streaming
        for step in agent_executor.stream(
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
    main()
