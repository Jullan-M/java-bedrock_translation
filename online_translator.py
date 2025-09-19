import asyncio

import aiohttp
import requests
from tqdm.asyncio import tqdm_asyncio

URL = "https://api.tartunlp.ai/translation/v2"

HEADERS = {
    "Content-Type": "application/json",
}

CONCURRENCY_LIMIT = 8  # Max concurrent requests


def neuro_translate(text, src_lang, tgt_lang):
    """
    Sends a POST request to the TartuNLP translation API and returns the translated text.

    :param text: string, text to translate
    :param src_lang: string, source language code (e.g., 'et')
    :param tgt_lang: string, target language code (e.g., 'en')
    :return: translated string, or raises an error
    """

    payload = {
        "text": text,
        "src": src_lang,
        "tgt": tgt_lang,
    }

    response = requests.post(URL, headers=HEADERS, json=payload)

    # Basic error handling
    if response.status_code != 200:
        raise Exception(
            f"Request failed (status {response.status_code}): {response.text}"
        )

    data = response.json()
    # Assuming API returns {"result": "translated text"}
    return data.get("result")


async def aio_translate(session, semaphore, text, src_lang, tgt_lang):
    payload = {
        "text": text,
        "src": src_lang,
        "tgt": tgt_lang,
    }

    async with semaphore:
        async with session.post(URL, headers=HEADERS, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(
                    f"Request failed (status {response.status}): {error_text}"
                )

            data = await response.json()
            return data.get("result")


async def translate_phrases(phrases, src_lang, tgt_lang):
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async with aiohttp.ClientSession() as session:
        tasks = [
            aio_translate(session, semaphore, p, src_lang, tgt_lang) for p in phrases
        ]

        try:
            translations = await tqdm_asyncio.gather(*tasks)
        except Exception as e:
            raise Exception(f"Translation error: {e}")
        return translations


if __name__ == "__main__":
    # Example usage:
    src = "nor"
    tgt = "sme"
    original_text = "Hei jeg håper du har det fint!"

    translation = neuro_translate(original_text, src, tgt)
    print("Original:", original_text)
    print("Translated:", translation)
