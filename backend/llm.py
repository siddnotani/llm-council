"""Provider-neutral API client for making LLM requests."""

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from .config import (
    COGNITION_API_KEY,
    COGNITION_API_URL,
    OPENROUTER_API_KEY,
    OPENROUTER_API_URL,
)


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0,
) -> Optional[Dict[str, Any]]:
    """
    Query a model through its configured provider.

    Models prefixed with ``cognition/`` are sent to Cognition with the
    prefix removed from the upstream model name. All other models are sent
    to OpenRouter unchanged.
    """
    if model.startswith("cognition/"):
        return await _query_cognition(
            model.removeprefix("cognition/"),
            messages,
            timeout,
        )
    return await _query_openrouter(model, messages, timeout)


async def _query_openrouter(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float,
) -> Optional[Dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    return await _query_provider(
        provider="OpenRouter",
        model=model,
        messages=messages,
        url=OPENROUTER_API_URL,
        headers=headers,
        timeout=timeout,
    )


async def _query_cognition(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float,
) -> Optional[Dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {COGNITION_API_KEY}",
        "Content-Type": "application/json",
    }
    return await _query_provider(
        provider="Cognition",
        model=model,
        messages=messages,
        url=COGNITION_API_URL,
        headers=headers,
        timeout=timeout,
    )


async def _query_provider(
    provider: str,
    model: str,
    messages: List[Dict[str, str]],
    url: str,
    headers: Dict[str, str],
    timeout: float,
) -> Optional[Dict[str, Any]]:
    payload = {
        "model": model,
        "messages": messages,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            message = data["choices"][0]["message"]
            return {
                "content": message.get("content"),
                "reasoning_details": message.get("reasoning_details"),
            }
    except Exception as e:
        print(f"Error querying {provider} model {model}: {e}")
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]],
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.

    Returns a mapping from each model identifier to its response, or None
    when that model's provider request failed.
    """
    tasks = [query_model(model, messages) for model in models]
    responses = await asyncio.gather(*tasks)
    return {model: response for model, response in zip(models, responses)}
