"""AI Agent Orchestrator — OpenAI-compatible tool-use loop (DeepSeek)."""

import json
from typing import Iterator

from openai import OpenAI

from dataprojection.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, MAX_TOOL_ROUNDS
from dataprojection.datasources.bridge import DataSource
from dataprojection.agent.system_prompt import build_system_prompt
from dataprojection.agent.tools.registry_openai import get_tool_definitions, execute_tool


class Orchestrator:
    """Manages a single AI conversation session."""

    def __init__(self, data_sources: list[DataSource] = None):
        self.data_sources = data_sources or []
        self.client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        self.system_prompt = build_system_prompt(self.data_sources)
        self.tools = get_tool_definitions()

    def chat(self, user_message: str, history: list[dict] = None) -> dict:
        """Process user message through tool-use loop.

        Returns:
            {"text", "chart_spec", "chart_type", "chart_specs": [dict],
             "dashboard_config": dict|None, "token_usage", "tool_calls_made", "error"}
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        result = {
            "text": "", "chart_spec": None, "chart_type": None,
            "chart_specs": [], "dashboard_config": None,
            "token_usage": {"input": 0, "output": 0},
            "tool_calls_made": [], "error": None,
        }

        total_in, total_out, last_query = 0, 0, None

        try:
            for _round in range(MAX_TOOL_ROUNDS):
                response = self.client.chat.completions.create(
                    model=LLM_MODEL, messages=messages,
                    tools=self.tools, temperature=0.7,
                )
                choice = response.choices[0]
                msg = choice.message
                total_in += response.usage.prompt_tokens or 0
                total_out += response.usage.completion_tokens or 0

                if not msg.tool_calls:
                    result["text"] = msg.content or ""
                    break

                # Track text and tool calls
                result["text"] = msg.content or ""

                tc_data = []
                for tc in msg.tool_calls:
                    tc_data.append({
                        "id": tc.id or "", "type": "function",
                        "function": {"name": tc.function.name,
                                     "arguments": tc.function.arguments},
                    })

                assistant_entry = {"role": "assistant", "content": msg.content or ""}
                assistant_entry["tool_calls"] = tc_data
                messages.append(assistant_entry)

                # Execute tools
                for tc in msg.tool_calls:
                    name = tc.function.name
                    try:
                        inp = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        inp = {}

                    result["tool_calls_made"].append(name)
                    output = execute_tool(name, inp)
                    output_str = output if isinstance(output, str) else str(output)

                    if name == "query_database":
                        last_query = {
                            "db_name": inp.get("db_name", ""),
                            "sql_query": inp.get("sql_query", ""),
                        }

                    if name == "generate_chart":
                        try:
                            out = json.loads(output_str)
                            if "chart_spec" in out:
                                ce = {
                                    "title": inp.get("title", "图表"),
                                    "chart_type": inp.get("chart_type", "bar"),
                                    "x_field": inp.get("x_field", ""),
                                    "y_field": inp.get("y_field", ""),
                                    "x_type": inp.get("x_type", "nominal"),
                                    "y_type": inp.get("y_type", "quantitative"),
                                    "color_field": inp.get("color_field", ""),
                                    "chart_spec": out["chart_spec"],
                                    "sql": last_query,
                                }
                                result["chart_specs"].append(ce)
                                result["chart_spec"] = out["chart_spec"]
                                result["chart_type"] = out.get("chart_type", "altair")
                        except (json.JSONDecodeError, KeyError):
                            pass

                    if name == "save_dashboard":
                        config = dict(inp)
                        if not config.get("charts") and result["chart_specs"]:
                            config["charts"] = result["chart_specs"]
                        result["dashboard_config"] = config

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": output_str,
                    })

            else:
                result["text"] = "（已达到最大工具调用轮次）"

            result["token_usage"] = {"input": total_in, "output": total_out}

        except Exception as e:
            result["error"] = f"AI 服务错误: {e}"

        return result


def create_orchestrator() -> Orchestrator:
    from dataprojection.datasources.bridge import get_liangke_historical
    return Orchestrator(data_sources=[get_liangke_historical()])
