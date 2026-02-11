from pydantic import BaseModel, Field


class SystemPromptsModel(BaseModel):
    """System Prompts for Workflow Models"""

    guardrail_prompt: str = Field(description="System Prompt for the Guardrail Model")
    query_writer_prompt: str = Field(
        description="System Prompt for the Query Writer Model"
    )
    responder_prompt: str = Field(description="System Prompt for the Responder Model")


class GuardrailStructuredOutputModel(BaseModel):
    """Structured output model for the Guardrail node"""

    is_irrelevant_prompt: bool = Field(
        description="True if the query is unrelated to NYC 311 data analysis, False otherwise."
    )
    is_mallicious_prompt: bool = Field(
        description="True if the message is malicious or harmful, False otherwise."
    )
    reason: str = Field(
        description="Explanation for blocking the message, empty if allowed."
    )


class QueryRunnerInputModel(BaseModel):
    """Input schema for the query_runner tool"""

    query: str = Field(description="The PostgreSQL SELECT query to execute")
