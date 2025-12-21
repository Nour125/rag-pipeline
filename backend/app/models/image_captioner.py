import base64

from openai import OpenAI


# ---- LM Studio Client ----

def get_lmstudio_client() -> OpenAI:
    """
    Returns an OpenAI-compatible client that talks to LM Studio.
    LM Studio must be running as a server on localhost:1234.
    """
    client = OpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",  # LM Studio akzeptiert beliebigen String als Key
    )
    return client


def _build_image_data_url(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """
    Encodes raw image bytes as a data URL usable by the vision model.
    """
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


def caption_image_with_qwen_vl(
    image_bytes: bytes,
    *,
    model: str = "qwen/qwen3-vl-4b",
    language: str = "en",
    max_tokens: int = 220,
) -> str:
    """
    Sends an image to LM Studio (Qwen3-VL) and asks for a detailed description.

    Args:
        image_bytes: Raw bytes of the image.
        model: Model id in LM Studio.
        language: 'en' or 'de' language of the caption.
        max_tokens: Maximum tokens for the response.

    Returns:
        A text description of the image.
    """
    client = get_lmstudio_client()
    image_data_url = _build_image_data_url(image_bytes)

    if language == "de":
        user_instruction = (
            "Beschreibe dieses Bild sehr detailliert. "
            "Erkläre, was darauf zu sehen ist, welche Personen, Objekte oder "
            "Situationen dargestellt sind und welche Aussage das Bild im Kontext "

            "Nutze vollständige Sätze und vermeide Spekulationen, wenn die Informationen "
            "nicht aus dem Bild hervorgehen."
        )
    else:
        user_instruction = (
            "Describe this image in a detailed way. "
            "Explain what is visible, which people, objects or scenes are shown, "
            "and what the image might convey in the context  "
            "Use full sentences and avoid speculation if the information is not visible."
        )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": user_instruction,
                    },
                    {
                        "type": "input_image",
                        "image_url": {
                            "url": image_data_url,
                        },
                    },
                ],
            }
        ],
        max_tokens=max_tokens,
        temperature=0.2,
    )

    # Bei OpenAI-kompatiblem Response ist die Antwort meist:
    # choices[0].message.content = [{"type": "output_text", "text": "..."}]
    msg_content = response.choices[0].message.content

    if isinstance(msg_content, str):
        # fallback für ältere Clients
        return msg_content.strip()

    # Neuere Form: Liste von Content-Parts
    for part in msg_content:
        if isinstance(part, dict):
            if part.get("type") in ("output_text", "text", "message"):
                text = part.get("text")
                if text:
                    return text.strip()

    # Fallback: alles als String zusammenbauen
    return str(msg_content)  #TODO vllt das weg machen und den msg_content returnen
