import yagmail

def send_email_smtp(
    sender_email: str,
    sender_password: str,
    recipient: str,
    subject: str,
    html_body: str,
    attachments: list | None = None,
):
    """
    Sends an HTML email via Gmail SMTP using yagmail.
    - html_body: fully inlined HTML string
    - attachments: list of yagmail.inline(...) or file-like objects
    """
    yag = yagmail.SMTP(
        user=sender_email,
        password=sender_password,
        host="smtp.gmail.com",
        port=587,
        smtp_starttls=True,
        smtp_ssl=False,
    )

    # Wrap HTML into a raw part
    html_part = yagmail.raw(html_body, "text/html")
    contents = [html_part]

    if attachments:
        contents.extend(attachments)

    yag.send(to=recipient, subject=subject, contents=contents)
