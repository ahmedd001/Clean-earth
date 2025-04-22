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
    - html_body should be a full HTML string.
    - attachments can be a list of inlines (yagmail.inline) or file-like objects.
    """
    yag = yagmail.SMTP(
        user=sender_email,
        password=sender_password,
        host="smtp.gmail.com",
        port=587,
        smtp_starttls=True,
        smtp_ssl=False,
    )

    # Let yagmail detect HTML from the first string item
    contents = [html_body]

    # tack on any inline images or attachments
    if attachments:
        contents.extend(attachments)

    yag.send(to=recipient, subject=subject, contents=contents)
