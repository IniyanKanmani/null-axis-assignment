from asyncio import run

import asyncpg
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, ToolMessage

from src.settings import Settings
from src.workflow import Workflow


async def main():
    settings = Settings()
    db_pool = await asyncpg.create_pool(
        host=settings.database_host,
        port=settings.database_port,
        database=settings.database_name,
        user=settings.database_user,
        password=settings.database_password.get_secret_value(),
        min_size=1,
        max_size=2,
    )

    workflow = Workflow(settings, db_pool)
    workflow.build_graph()

    astream = workflow.astream(
        messages=[
            HumanMessage(
                content="What are the top 10 complaint types by number of records?",
            ),
        ],
    )

    async for _, m in astream:
        if settings.debug:
            if isinstance(m[0], AIMessageChunk):
                print(m[0].content, end="", flush=True)
            elif isinstance(m[0], AIMessage):
                if m[0].tool_calls:
                    print(m[0].tool_calls)
                else:
                    print(m[0].content)
            elif isinstance(m[0], ToolMessage):
                print(m[0].content)


if __name__ == "__main__":
    run(main())
