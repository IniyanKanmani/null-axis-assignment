from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from typing_extensions import AsyncIterator, Literal, Optional

from src.settings import Settings
from src.state import WorkflowState


class Workflow:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def setup_models(self) -> None:
        self.guardrail_model = ChatOpenAI(
            base_url=self.settings.openrouter_base_url,
            api_key=self.settings.openrouter_api_key,
            model=self.settings.openrouter_model_1,
            disable_streaming=True,
            streaming=False,
            temperature=0.25,
            extra_body={
                "provider": {
                    "allow_fallbacks": True,
                    "require_parameters": True,
                    "data_collection": "deny",
                    "zdr": True,
                    "sort": "latency",
                },
            },
        )

        self.query_writer_model = ChatOpenAI(
            base_url=self.settings.openrouter_base_url,
            api_key=self.settings.openrouter_api_key,
            model=self.settings.openrouter_model_2,
            disable_streaming=True,
            streaming=False,
            temperature=0.25,
            extra_body={
                "provider": {
                    "allow_fallbacks": True,
                    "require_parameters": True,
                    "data_collection": "deny",
                    "zdr": True,
                    "sort": "latency",
                },
            },
        )

        self.answer_model = ChatOpenAI(
            base_url=self.settings.openrouter_base_url,
            api_key=self.settings.openrouter_api_key,
            model=self.settings.openrouter_model_3,
            disable_streaming=False,
            streaming=True,
            temperature=0.75,
            extra_body={
                "provider": {
                    "allow_fallbacks": True,
                    "require_parameters": True,
                    "data_collection": "deny",
                    "zdr": True,
                    "sort": "latency",
                },
            },
        )

    async def guardrail_node(self, state: WorkflowState) -> Optional[WorkflowState]:
        pass

    def router(self, state: WorkflowState) -> Literal["query_writer", "end"]:
        # Temp
        if True:
            return "query_writer"
        else:
            return "end"

    async def query_writer_node(self, state: WorkflowState) -> Optional[WorkflowState]:
        pass

    async def answer_node(self, state: WorkflowState) -> Optional[WorkflowState]:
        pass

    def build_graph(self) -> None:
        graph_builder = StateGraph(WorkflowState)

        graph_builder.add_node("guardrail", self.guardrail_node)
        graph_builder.add_node("query_writer", self.query_writer_node)
        graph_builder.add_node("answer", self.answer_node)

        graph_builder.add_edge(START, "guardrail")
        graph_builder.add_conditional_edges(
            "router",
            self.router,
            {
                "query_writer": "query_writer",
                "end": END,
            },
        )
        graph_builder.add_edge("query_writer", "answer")
        graph_builder.add_edge("answer", END)

        self.graph_builder = graph_builder

    def astream(self, messages: list[BaseMessage]) -> AsyncIterator[dict]:
        graph = self.graph_builder.compile()
        state = WorkflowState(messages=messages)

        return graph.astream(input=state, stream_mode=["messages"])
