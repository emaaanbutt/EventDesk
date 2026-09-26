import httpx

from app.core.config import settings


async def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    html_content: str,
) -> str:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={"api-key": settings.BREVO_API_KEY},
            json={
                "sender": {
                    "email": settings.BREVO_SENDER_EMAIL,
                    "name": settings.BREVO_SENDER_NAME,
                },
                "to": [{"email": to_email, "name": to_name}],
                "subject": subject,
                "htmlContent": html_content,
            },
        )
    response.raise_for_status()
    try:
        message_id = response.json()["messageId"]
    except (ValueError, KeyError, TypeError):
        raise ValueError("Brevo response did not include a message ID") from None
    if not isinstance(message_id, str) or not message_id:
        raise ValueError("Brevo response did not include a message ID")
    return message_id
