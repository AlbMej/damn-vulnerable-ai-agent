import json
import os
import inspect
from typing import Any
import httpx

from fastapi import Request

LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:8000/v1")
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "not-needed")
MODEL_NAME: str = os.getenv("MODEL_NAME", "qwen3-4b")

def _auth_headers() -> dict[str, str]:
    if LLM_API_KEY and LLM_API_KEY != "not-needed":
        return {"Authorization": f"Bearer {LLM_API_KEY}"}
    return {}

def _get_active_model() -> str:
    try:
        url = f"{LLM_BASE_URL.rstrip('/')}/models"
        with httpx.Client(timeout=2.0) as client:
            resp = client.get(url, headers=_auth_headers())
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                if data and isinstance(data, list) and "id" in data[0]:
                    return data[0]["id"]
    except Exception:
        pass
    return MODEL_NAME

def chat_completion(messages: list[dict[str, Any]], tools_schema: list[dict[str, Any]]) -> dict[str, Any]:
    url = f"{LLM_BASE_URL.rstrip('/')}/chat/completions"
    payload: dict[str, Any] = {
        "model": _get_active_model(),
        "messages": messages,
        "tools": tools_schema,
        "temperature": 0.7,
    }
    with httpx.Client(timeout=120.0) as client:
        resp = client.post(url, json=payload, headers=_auth_headers())
        resp.raise_for_status()
    return resp.json()

def execute_tool_call(name: str, arguments: dict[str, Any], tool_functions: dict[str, Any], request: Request = None) -> str:
    fn = tool_functions.get(name)
    if fn is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    
    sig = inspect.signature(fn)
    if "request" in sig.parameters and request is not None:
        arguments["request"] = request
        
    result = fn(**arguments)
    return json.dumps(result) if isinstance(result, dict) else str(result)

def handle_assistant_response(system_prompt: str, history: list[dict[str, Any]], tools_schema: list[dict[str, Any]], tool_functions: dict[str, Any], request: Request = None) -> list[dict[str, Any]]:
    new_items = []
    
    # Note: Falling back to a single response swap due to streaming complexity with HTMX + nested tool executions.
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        if msg["role"] == "tool":
            messages.append({
                "role": "tool",
                "tool_call_id": msg["tool_call_id"],
                "content": msg["content"],
            })
        elif msg["role"] == "assistant" and "tool_calls" in msg:
            messages.append({
                "role": "assistant",
                "content": msg.get("content") or "",
                "tool_calls": msg["tool_calls"],
            })
        else:
            messages.append({"role": msg["role"], "content": msg.get("content", "")})
    
    while True:
        raw = chat_completion(messages, tools_schema)
        choice = raw["choices"][0]
        assistant_msg = choice["message"]
        finish_reason = choice.get("finish_reason", "stop")
        
        tool_calls = assistant_msg.get("tool_calls")
        if tool_calls:
            history_entry = {
                "role": "assistant",
                "content": assistant_msg.get("content") or "",
                "tool_calls": tool_calls,
            }
            history.append(history_entry)
            new_items.append(history_entry)
            messages.append(history_entry)
            
            for tc in tool_calls:
                fn_name = tc["function"]["name"]
                fn_args = json.loads(tc["function"]["arguments"])
                tool_result = execute_tool_call(fn_name, fn_args, tool_functions, request)
                
                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": fn_name,
                    "content": tool_result,
                    "arguments": tc["function"]["arguments"]
                }
                history.append(tool_msg)
                new_items.append(tool_msg)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": tool_result,
                })
            
            if finish_reason == "tool_calls":
                continue
            break
        else:
            text = assistant_msg.get("content", "")
            final_msg = {"role": "assistant", "content": text}
            history.append(final_msg)
            new_items.append(final_msg)
            break
            
    return new_items
