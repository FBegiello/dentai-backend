import base64
import os
from openai import OpenAI

from agents import function_tool, FunctionTool, FileSearchTool
from agents import Agent, Runner
from openai.resources.vector_stores.vector_stores import VectorStore


from app.schemas.response_schema import Tooth, TOOTH_MAPPING
from app.schemas.prompts import (
    WORKER_TOOTH_IDENTIFIER,
    WORKER_NOTETAKER,
    AGENT_PROMPT,
    AUDIO_GENERATOR_PROMPT,
)

from app.core.config import settings


class DentalAgentManager:
    action_buffer: list[Tooth] = []
    visit_transcript: str = ""

    def __init__(self):

        self.vector_store: VectorStore = self.initialize_rag(
            data_path=settings.DATA_PATH, kb_name="patient_dental_history"
        )

        self.tool_dental_history: FileSearchTool = FileSearchTool(
            vector_store_ids=[self.vector_store.id], max_num_results=3
        )

        self.tool_fill_chart: FunctionTool = function_tool(
            self.mark_tooth,
            name_override="mark_tooth_condition",
            description_override="A tool for marking patient teeth state on a chart. "
            "Should be called when receiving instructions about teeth state.",
        )

        self.dental_agent = Agent(
            name="Dental assistant",
            model=settings.LLM_MODEL,
            instructions=AGENT_PROMPT,
            tools=[self.tool_fill_chart, self.tool_dental_history],
        )

    def mark_tooth(self, input: str):
        response = settings.OPENAI_CLIENT.responses.parse(
            model=settings.LLM_MODEL_WORKERS,
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
        self.action_buffer.append(response.output_parsed)

    def flush_buffer(
        self,
    ) -> list[Tooth] | None:
        if self.action_buffer:
            buffer_state = self.action_buffer
            self.action_buffer = []
            for tooth in buffer_state:
                print((tooth.position.value - 1), tooth.jaw, tooth.side)
                tooth.position = TOOTH_MAPPING[tooth.jaw][tooth.side][
                    (tooth.position.value - 1)
                ]
                # tooth.position = tooth.position.value - 1
                print(tooth.position)
            return buffer_state
        else:
            return None

    def create_file(self, client: OpenAI, file_path: str):
        with open(file_path, "rb") as file_content:
            result = client.files.create(file=file_content, purpose="assistants")
        return result.id

    def initialize_rag(self, data_path: str, kb_name: str) -> VectorStore:
        print("Setting up RAG")
        file_id = self.create_file(settings.OPENAI_CLIENT, settings.DATA_PATH)

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

    def add_to_transcript(self, message: str, role: str):
        self.visit_transcript += f"**{role}**\n message\n"

    def generate_transcript(self):
        response = settings.OPENAI_CLIENT.responses.create(
            model=settings.LLM_MODEL_COMPLEX,
            input=WORKER_NOTETAKER + self.visit_transcript,
        )
        return response

    def generate_audio_response(
        self, message: str, temp_file_path: str = settings.TEMP_AUDIO_PATH
    ) -> bytes:
        with settings.OPENAI_CLIENT.audio.speech.with_streaming_response.create(
            model=settings.LLM_MODEL_TTS,
            voice=settings.LLM_MODEL_TTS_VOICE,
            input=message,
            instructions=AUDIO_GENERATOR_PROMPT,
        ) as response:
            response.stream_to_file(temp_file_path)

        with open(temp_file_path, "rb") as audio_file:
            read_file = audio_file.read()
            audio_bytes = base64.b64encode(read_file)
        os.remove(temp_file_path)

        return audio_bytes

    async def query_agent_text_mode(self, query: str) -> str:
        result = await Runner.run(self.dental_agent, query)
        print(f"Agent output -> {result.final_output}")
        return result.final_output
