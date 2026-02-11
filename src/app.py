import asyncio
import json

import streamlit as st
from langchain_core.messages import AIMessage, AIMessageChunk

from settings import Settings
from workflow import Workflow

_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)


async def initialize_workflow():
    settings = Settings()

    workflow = Workflow(settings)
    workflow.build_graph()

    return workflow, settings


def run_async(coro):
    return _loop.run_until_complete(coro)


def main():
    st.set_page_config(
        page_title="NYC 311 Analytics Bot",
        page_icon="🏙️",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        .main {
            padding: 2rem;
        }
        .stChatMessage {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background-color: #e3f2fd;
        }
        .stChatMessage[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
            background-color: #f5f5f5;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "workflow" not in st.session_state:
        with st.spinner("Initializing bot..."):
            try:
                workflow, settings = run_async(initialize_workflow())

                st.session_state.workflow = workflow
                st.session_state.settings = settings
            except Exception as e:
                st.error(f"Failed to initialize: {e}")
                st.stop()

    if not st.session_state.messages:
        st.title("🏙️ NYC 311 Analytics Bot")

        st.markdown(
            "Ask questions about NYC 311 service request data from 2020 to present."
        )

    with st.sidebar:
        st.header("ℹ️ About")

        st.markdown("""
        This bot analyzes NYC 311 service request data to provide insights about:
        - 📊 Complaint types and statistics
        - 🏢 Agency performance
        - 📍 Geographic patterns
        - ⏱️ Resolution times
        - 📈 Trends over time
        """)

        st.header("💡 Example Questions")

        example_questions = [
            "What are the top 10 complaint types by number of records?",
            "For the top 5 complaint types, what percent were closed within 3 days?",
            "Which ZIP code has the highest number of complaints?",
            "What proportion of complaints include a valid latitude/longitude?",
            "Which agency has the slowest average resolution time?",
            "Compare noise complaints in 2020 versus 2023",
        ]

        for i, question in enumerate(example_questions):
            if st.button(f"{i + 1}. {question[:40]}...", key=f"example_{i}"):
                st.session_state.current_input = question
                st.rerun()

        st.divider()

        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant" and "metadata" in message:
                with st.expander("📊 View Query Details"):
                    metadata = message["metadata"]

                    if "is_irrelevant_prompt" in metadata:
                        st.write(f"**Irrelevant:** {metadata['is_irrelevant_prompt']}")
                    if "is_mallicious_prompt" in metadata:
                        st.write(f"**Malicious:** {metadata['is_mallicious_prompt']}")

                    if "sql_query" in metadata:
                        st.code(metadata["sql_query"], language="sql")

    def process_prompt(prompt: str):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()

            try:
                workflow = st.session_state.workflow
                settings = st.session_state.settings

                full_response = ""
                guardrail_data = None
                sql_query = None

                astream = workflow.astream(prompt, st.session_state.messages)

                async def process_stream():
                    nonlocal full_response, guardrail_data, sql_query

                    async for _, data in astream:
                        if isinstance(data, tuple) and len(data) > 0:
                            msg = data[0]

                            if isinstance(msg, AIMessageChunk):
                                if settings.debug:
                                    print(msg.content, end="", flush=True)

                                if msg.content and isinstance(msg.content, str):
                                    full_response += msg.content
                                    response_placeholder.markdown(full_response + "▌")

                            elif isinstance(msg, AIMessage):
                                if settings.debug:
                                    if msg.content:
                                        print(msg.content)

                                if msg.content and isinstance(msg.content, str):
                                    try:
                                        content_dict = json.loads(msg.content)
                                        if "is_irrelevant_prompt" in content_dict:
                                            guardrail_data = {
                                                "is_irrelevant_prompt": content_dict[
                                                    "is_irrelevant_prompt"
                                                ],
                                                "is_mallicious_prompt": content_dict[
                                                    "is_mallicious_prompt"
                                                ],
                                            }

                                            if content_dict.get(
                                                "is_irrelevant_prompt"
                                            ) or content_dict.get(
                                                "is_mallicious_prompt"
                                            ):
                                                full_response = content_dict.get(
                                                    "reason", ""
                                                )
                                                return full_response

                                    except Exception:
                                        pass

                                if hasattr(msg, "tool_calls") and msg.tool_calls:
                                    if settings.debug:
                                        print(msg.tool_calls)

                                    for tool_call in msg.tool_calls:
                                        if tool_call.get("name") == "query_runner":
                                            args = tool_call.get("args", {})
                                            sql_query = args.get("query", "")

                            elif hasattr(msg, "content") and isinstance(
                                msg.content, list
                            ):
                                for item in msg.content:
                                    if isinstance(item, dict) and "text" in item:
                                        try:
                                            raw_results = json.loads(item["text"])
                                            if settings.debug:
                                                print(raw_results)
                                        except Exception:
                                            if settings.debug:
                                                print(item["text"])

                    return full_response + "\n"

                final_response = run_async(process_stream())

                if settings.debug:
                    print()

                response_placeholder.markdown(final_response)

                metadata = {}

                if guardrail_data:
                    metadata["is_irrelevant_prompt"] = guardrail_data[
                        "is_irrelevant_prompt"
                    ]
                    metadata["is_mallicious_prompt"] = guardrail_data[
                        "is_mallicious_prompt"
                    ]

                if sql_query:
                    metadata["sql_query"] = sql_query

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": final_response,
                        "metadata": metadata if metadata else None,
                    }
                )
                st.rerun()

            except Exception as e:
                error_msg = f"❌ Error processing your request: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )

    if "current_input" in st.session_state:
        prompt = st.session_state.current_input
        del st.session_state.current_input

        process_prompt(prompt)

    elif prompt := st.chat_input(
        "What would you like to know about NYC 311 data?", key="chat_input"
    ):
        process_prompt(prompt)


if __name__ == "__main__":
    main()
