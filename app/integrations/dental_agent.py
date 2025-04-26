from openai import OpenAI

from agents import function_tool, FunctionTool, FileSearchTool
from agents import Agent, Runner
from openai.resources.vector_stores.vector_stores import VectorStore

from app.schemas.response_schema import Tooth
from app.schemas.prompts import WORKER_TOOTH_IDENTIFIER, AGENT_PROMPT

from app.core.config import settings


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


class DentalAgentManager:
    def __init__(self):

        self.vector_store: VectorStore = self.initialize_rag(
            data_path="./data/dent-hist.md", kb_name="patient_dental_history"
        )

        self.tool_dental_history: FileSearchTool = FileSearchTool(
            vector_store_ids=[self.vector_store.id], max_num_results=3
        )

        self.tool_fill_chart: FunctionTool = function_tool(
            mark_tooth,
            name_override="mark_tooth_condition",
            description_override="A tool for marking patient teeth state on a chart. "
            "Should be called when receiving instructions about teeth state.",
        )

        self.dental_agent = Agent(
            name="Dental assistant",
            instructions=AGENT_PROMPT,
            tools=[self.tool_fill_chart, self.tool_dental_history],
        )

    def create_file(self, client: OpenAI, file_path: str):
        with open(file_path, "rb") as file_content:
            result = client.files.create(file=file_content, purpose="assistants")
        return result.id

    def initialize_rag(self, data_path: str, kb_name: str) -> VectorStore:
        print("Setting up RAG")
        file_id = self.create_file(settings.OPENAI_CLIENT, "./data/dent-hist.md")

        vector_store = settings.OPENAI_CLIENT.vector_stores.create(
            name="dental_history"
        )
        settings.OPENAI_CLIENT.vector_stores.files.create(
            vector_store_id=vector_store.id, file_id=file_id
        )

        result = settings.OPENAI_CLIENT.vector_stores.files.list(
            vector_store_id=vector_store.id
        )

        print(result)

        return vector_store

    async def query_agent_text_mode(self, query: str) -> str:
        result = Runner.run(self.dental_agent, query)
        print(f"Agent output -> {result.final_output}")
        return result.final_output
