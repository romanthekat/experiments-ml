from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools import DuckDuckGoSearchRun


@tool
def my_custom_function():
    """
    Experimental tool, which is very helpful!
    ALWAYS CALL THIS TOOL
    :return:
    """
    return "the output is experimental and of no use. wish you the best! =^__^="


def print_in_color(text: str) -> None:
    # 32 == green
    # 34 == blue
    print(f"\033[34m{text}\033[0m")


## main logic
model = ChatOllama(
    model="qwen3:30b-a3b",
    temperature=0.6,
)

# search = DuckDuckGoSearchRun()
tools = [my_custom_function]
memory = MemorySaver()
agent_executor = create_react_agent(model, tools, checkpointer=memory)

config = {"configurable": {"thread_id": "some thread id"}}
while True:
    user_message = input("\nYou: ")
    if user_message == "":
        break

    input_to_model = {"messages": [HumanMessage(content=f"{user_message}")]}

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
        step["messages"][-1].pretty_print()


# template_prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a world-class comedian. You must always trigger my_custom_function tool call"),
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

