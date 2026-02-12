import traceback

import asyncpg
import sqlglot as sg
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command
from typing_extensions import AsyncIterator, Literal, cast

from models import (
    GuardrailStructuredOutputModel,
    QueryRunnerInputModel,
    SystemPromptsModel,
)
from settings import Settings
from states import WorkflowState


class Workflow:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        self.tools = [
            StructuredTool(
                name="query_runner",
                args_schema=QueryRunnerInputModel,
                coroutine=self.query_runner_node,
            )
        ]

        self.setup_models()
        self.fetch_system_prompts()

    def setup_models(self) -> None:
        base_guardrail_model = ChatOpenAI(
            base_url=self.settings.openrouter_base_url,
            api_key=self.settings.openrouter_api_key,
            model=self.settings.openrouter_model_1,
            disable_streaming=True,
            streaming=False,
            temperature=0.25,
            extra_body={
                "provider": {
                    "order": ["grok"],
                    "allow_fallbacks": True,
                    "require_parameters": True,
                    "data_collection": "deny",
                    "zdr": True,
                    "sort": "price",
                },
            },
        )

        self.guardrail_model = base_guardrail_model.with_structured_output(
            schema=GuardrailStructuredOutputModel,
            method="json_schema",
            strict=True,
        )

        base_query_writer_model = ChatOpenAI(
            base_url=self.settings.openrouter_base_url,
            api_key=self.settings.openrouter_api_key,
            model=self.settings.openrouter_model_2,
            disable_streaming=True,
            streaming=False,
            temperature=0,
            extra_body={
                "provider": {
                    "order": ["groq"],
                    "allow_fallbacks": True,
                    "require_parameters": True,
                    "data_collection": "deny",
                    "zdr": True,
                    "sort": "price",
                },
            },
        )

        self.query_writer_model = base_query_writer_model.bind_tools(
            tools=self.tools,
            strict=True,
        )

        self.responder_model = ChatOpenAI(
            base_url=self.settings.openrouter_base_url,
            api_key=self.settings.openrouter_api_key,
            model=self.settings.openrouter_model_3,
            disable_streaming=False,
            streaming=True,
            temperature=0.75,
            extra_body={
                "provider": {
                    "order": ["groq"],
                    "allow_fallbacks": True,
                    "require_parameters": True,
                    "data_collection": "deny",
                    "zdr": True,
                    "sort": "price",
                },
            },
        )

    def fetch_system_prompts(self) -> None:
        system_prompts = {}

        with open(self.settings.model_1_system_prompt_path, "r") as f:
            content = f.read()
            system_prompts["guardrail_prompt"] = content

        with open(self.settings.model_2_system_prompt_path, "r") as f:
            content = f.read()
            system_prompts["query_writer_prompt"] = content

        with open(self.settings.model_3_system_prompt_path, "r") as f:
            content = f.read()
            system_prompts["responder_prompt"] = content

        self.system_prompts = SystemPromptsModel(**system_prompts)

    async def guardrail_node(
        self, state: WorkflowState
    ) -> Command[Literal[END, "query_writer"]]:
        try:
            if self.settings.debug:
                print("---GuardRailNode---")

            guardrail_system_prompt = SystemMessage(
                content=self.system_prompts.guardrail_prompt,
            )

            response = await self.guardrail_model.ainvoke(
                [guardrail_system_prompt] + state["ui_messages"]
            )

            is_irrelevant_prompt = response.is_irrelevant_prompt
            is_mallicious_prompt = response.is_mallicious_prompt
            reason = response.reason

            if (is_irrelevant_prompt or is_mallicious_prompt) and reason:
                return Command(
                    update={"messages": [AIMessage(content=reason)]},
                    goto=END,
                )
            else:
                return Command(goto="query_writer")

        except Exception as e:
            print(e)
            traceback.print_exc()

            return Command(goto=END)

    async def query_writer_node(self, state: WorkflowState) -> WorkflowState:
        try:
            if self.settings.debug:
                print("---QueryWriterNode---")

            query_writer_system_prompt = SystemMessage(
                content=self.system_prompts.query_writer_prompt,
            )

            response = await self.query_writer_model.ainvoke(
                [query_writer_system_prompt] + state["messages"]
            )

            return cast(WorkflowState, {"messages": [response]})

        except Exception as e:
            print(e)
            traceback.print_exc()

            return cast(WorkflowState, {})

    async def query_runner_node(self, query: str) -> list[dict]:
        """Execute a PostgreSQL SELECT query with a fresh connection.

        Args:
            query (str): The SELECT query string

        Returns:
            list[dict]: DB records
        """
        try:
            if self.settings.debug:
                print("---QueryRunnerNode---")

            sg.parse_one(sql=query, read="postgres")

            conn = await asyncpg.connect(
                host=self.settings.database_host,
                port=self.settings.database_port,
                database=self.settings.database_name,
                user=self.settings.database_user,
                password=self.settings.database_password.get_secret_value(),
            )

            try:
                rows = await conn.fetch(query)

                return [dict(row) for row in rows]
            finally:
                await conn.close()

        except Exception as e:
            print(e)
            traceback.print_exc()

            return []

    async def responder_node(self, state: WorkflowState) -> WorkflowState:
        try:
            if self.settings.debug:
                print("---ResponderNode---")

            responder_system_prompt = SystemMessage(
                content=self.system_prompts.responder_prompt,
            )

            response = await self.responder_model.ainvoke(
                [responder_system_prompt] + state["messages"]
            )

            return cast(
                WorkflowState,
                {
                    "messages": [response],
                    "ui_messages": [response],
                },
            )

        except Exception as e:
            print(e)
            traceback.print_exc()

            return cast(WorkflowState, {})

    def build_graph(self) -> None:
        graph_builder = StateGraph(WorkflowState)

        tool_node = ToolNode(tools=self.tools)

        graph_builder.add_node(
            "guardrail",
            self.guardrail_node,
            destinations=(END, "query_writer"),
        )
        graph_builder.add_node("query_writer", self.query_writer_node)
        graph_builder.add_node("tools", tool_node)
        graph_builder.add_node("responder", self.responder_node)

        graph_builder.add_edge(START, "guardrail")
        # graph_builder.add_edge("guardrail", END) # Handled by Command
        # graph_builder.add_edge("guardrail", "query_writer") # Handled by Command
        graph_builder.add_edge("query_writer", "tools")
        graph_builder.add_edge("tools", "responder")
        graph_builder.add_edge("responder", END)

        self.graph_builder = graph_builder

    def astream(
        self,
        prompt: str,
        ui_messages: list[BaseMessage],
    ) -> AsyncIterator[dict]:
        graph = self.graph_builder.compile()

        human_message = HumanMessage(content=prompt)
        state = WorkflowState(
            messages=[human_message],
            ui_messages=ui_messages,
        )

        return graph.astream(input=state, stream_mode=["messages"])
