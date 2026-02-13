from typing import Optional

from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated, List, TypedDict


class WorkflowState(TypedDict):
    conversation_summary: Optional[AIMessage]
    messages: Annotated[List[BaseMessage], add_messages]
    ui_messages: Annotated[List[BaseMessage], add_messages]
