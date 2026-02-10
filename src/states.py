from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated, List, TypedDict


class WorkflowState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
