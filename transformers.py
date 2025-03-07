import os
import aiohttp
import asyncio
import random
from dotenv import load_dotenv
from openai import AzureOpenAI
from openai import OpenAI

# Load environment variables
load_dotenv()

# MODEL CATALOG

# AZURE: gpt4o_mini_async_azure
# AZURE: gpt4o_mini_azure
# AZURE: gpt35_1106_async
# OPENAI: gpt4o_async
# OPENAI: gpt4o_mini_async
# OPENAI: gpt35_1106
# OPENAI: gpt4o
# OPENAI: gpt4o_mini


# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1  # seconds
MAX_RETRY_DELAY = 10  # seconds

# Error classification
TEMPORARY_ERROR_MESSAGES = [
    "nodename nor servname provided, or not known",
    "Cannot connect to host",
    "Connection reset by peer",
    "Connection refused",
    "Timeout",
    "timeout",
    "Too Many Requests",
    "Rate limit",
    "Server is busy",
    "Service Unavailable",
    "Internal Server Error",
    "Bad Gateway",
    "Gateway Timeout",
]


def is_temporary_error(error_message):
    """
    Determines if an error is likely temporary and can be retried.

    Args:
        error_message (str): The error message string

    Returns:
        bool: True if the error is likely temporary, False otherwise
    """
    return any(msg in error_message for msg in TEMPORARY_ERROR_MESSAGES)


# ---Azure OpenAI---
async def gpt4o_mini_async_azure_with_retry(
    system,
    prompt,
    session: aiohttp.ClientSession,
    key,
    endpoint,
    max_retries=MAX_RETRIES,
):
    """
    Wrapper for gpt4o_mini_async_azure with retry logic for temporary failures.

    Args:
        system: System prompt
        prompt: User prompt
        session: aiohttp ClientSession
        key: API key
        endpoint: API endpoint URL
        max_retries: Maximum number of retry attempts

    Returns:
        tuple: (response content, usage info)

    Raises:
        Exception: If all retry attempts fail
    """
    retry_count = 0
    last_error = None

    while retry_count <= max_retries:
        try:
            return await gpt4o_mini_async_azure(system, prompt, session, key, endpoint)
        except Exception as e:
            last_error = e
            error_message = str(e)

            # If we've reached max retries or it's not a temporary error, raise the exception
            if retry_count >= max_retries or not is_temporary_error(error_message):
                raise

            # Calculate backoff with jitter
            delay = min(
                INITIAL_RETRY_DELAY * (2**retry_count) + random.uniform(0, 1),
                MAX_RETRY_DELAY,
            )

            # Log retry attempt
            print(
                f"Temporary error with endpoint {endpoint}: {error_message}. Retrying in {delay:.2f}s (attempt {retry_count+1}/{max_retries})"
            )

            # Wait before retrying
            await asyncio.sleep(delay)
            retry_count += 1

    # This should not be reached due to the raise in the loop, but just in case
    raise last_error


async def gpt4o_mini_async_azure(
    system, prompt, session: aiohttp.ClientSession, key, endpoint
):
    api_key = key
    azure_endpoint = endpoint
    # Construct the Azure OpenAI endpoint URL for chat completions
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    # Prepare the request data
    data = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }

    # Make the async request to Azure OpenAI
    async with session.post(azure_endpoint, headers=headers, json=data) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"Error calling Azure OpenAI API: {resp.status}, {text}")

        # Parse the response JSON
        response = await resp.json()

        # Return both the response content and usage information
        return response["choices"][0]["message"]["content"], response["usage"]


def gpt4o_mini_azure_with_retry(system, prompt, key, endpoint, max_retries=MAX_RETRIES):
    """
    Wrapper for gpt4o_mini_azure with retry logic for temporary failures.

    Args:
        system: System prompt
        prompt: User prompt
        key: API key
        endpoint: API endpoint URL
        max_retries: Maximum number of retry attempts

    Returns:
        list: [response content, usage info]

    Raises:
        Exception: If all retry attempts fail
    """
    retry_count = 0
    last_error = None

    while retry_count <= max_retries:
        try:
            return gpt4o_mini_azure(system, prompt, key, endpoint)
        except Exception as e:
            last_error = e
            error_message = str(e)

            # If we've reached max retries or it's not a temporary error, raise the exception
            if retry_count >= max_retries or not is_temporary_error(error_message):
                raise

            # Calculate backoff with jitter
            delay = min(
                INITIAL_RETRY_DELAY * (2**retry_count) + random.uniform(0, 1),
                MAX_RETRY_DELAY,
            )

            # Log retry attempt
            print(
                f"Temporary error with endpoint {endpoint}: {error_message}. Retrying in {delay:.2f}s (attempt {retry_count+1}/{max_retries})"
            )

            # Wait before retrying
            import time

            time.sleep(delay)
            retry_count += 1

    # This should not be reached due to the raise in the loop, but just in case
    raise last_error


def gpt4o_mini_azure(system, prompt, key, endpoint):
    # Initialize the Azure OpenAI client
    client = AzureOpenAI(
        api_key=key,
        api_version="2024-02-01",
        azure_endpoint=endpoint,
    )

    # Create a chat completion request
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        model="gpt-4o-mini",
    )

    # Access the content and usage information using dot notation
    content = response.choices[0].message.content  # Access using dot notation
    usage_info = response.usage  # Access usage using dot notation

    return [content, usage_info]


# ---OpenAI---
async def gpt35_1106_async(system, prompt, session):
    api_key = os.getenv("OPEN_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "model": "gpt-3.5-turbo-1106",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }

    async with session.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    ) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"Error calling OpenAI API: {resp.status}, {text}")
        response = await resp.json()
        return [response["choices"][0]["message"]["content"], response["usage"]]


async def gpt4o_async(system, prompt, session):
    api_key = os.getenv("OPEN_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }

    async with session.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    ) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"Error calling OpenAI API: {resp.status}, {text}")
        response = await resp.json()
        return [response["choices"][0]["message"]["content"], response["usage"]]


async def gpt4o_mini_async(system, prompt, session):
    api_key = os.getenv("OPEN_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }

    async with session.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    ) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"Error calling OpenAI API: {resp.status}, {text}")
        response = await resp.json()
        return [response["choices"][0]["message"]["content"], response["usage"]]


def gpt35_1106(system, prompt):
    client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        model="gpt-3.5-turbo-1106",
    )
    return [completion.choices[0].message.content, completion.usage]


def gpt4o(system, prompt):
    client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        model="gpt-4o",
    )
    return [completion.choices[0].message.content, completion.usage]


def gpt4o_mini(system, prompt):
    client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        model="gpt-4o-mini",
    )
    return [completion.choices[0].message.content, completion.usage]


# ---Anthropic---

# ---LLama---

# ---Gemma---

# ---Groq---
