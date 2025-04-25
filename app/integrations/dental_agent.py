from openai import OpenAI

# from agents import Agent, Runner, FileSearchTool, function_tool

from app.schemas.response_schema import Tooth
from app.schemas.prompts import WORKER_TOOTH_IDENTIFIER

from app.core.config import settings


def create_file(client: OpenAI, file_path: str):
    with open(file_path, "rb") as file_content:
        result = client.files.create(file=file_content, purpose="assistants")
    return result.id


def mark_tooth(input: str):
    response = settings.OPENAI_CLIENT.responses.parse(
        model="gpt-4o",
        input=[
            {"role": "system", "content": WORKER_TOOTH_IDENTIFIER},
            {
                "role": "user",
                "content": input,
            },
        ],
        text_format=Tooth,
    )
    print(response.output_parsed)
    # TODO - input mark chart here


def initialize_rag():

    file_id = create_file(settings.OPENAI_CLIENT, "./data/dent-hist.md")

    vector_store = settings.OPENAI_CLIENT.vector_stores.create(name="knowledge_base")
    settings.OPENAI_CLIENT.vector_stores.files.create(
        vector_store_id=vector_store.id, file_id=file_id
    )

    result = settings.OPENAI_CLIENT.vector_stores.files.list(
        vector_store_id=vector_store.id
    )

    print(result)

    return vector_store


# _tool_dental_history = FileSearchTool(
#     vector_store_ids=[vector_store.id], max_num_results=3
# )

# _tool_fill_chart = function_tool(
#     mark_tooth,
#     name_override="mark_tooth_condition",
#     description_override="A tool for marking patient teeth state on a chart. "
#     "Should be called when receiving instructions about teeth state.",
# )

# agent = Agent(
#     name="Dental assistant",
#     instructions=AGENT_PROMPT,
#     tools=[_tool_fill_chart, _tool_dental_history],
# )

# result = Runner.run_sync(agent, "Cavity in distal left eight in upper jaw")
# print(result.final_output)

# print(result)
