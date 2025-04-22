# utils/email_sender.py
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
    - html_body should be a full HTML string (starting with <!DOCTYPE html> or <html>).
    - attachments can be a list of yagmail.inline(...) or file‑like objects.
    """
    # 1) connect
    yag = yagmail.SMTP(user=sender_email, password=sender_password)

    # 2) build contents: start with your HTML
    contents = [html_body]

    # 3) tack on any attachments (including inline images)
    if attachments:
        contents.extend(attachments)

    # 4) send; yagmail will see the '<' in html_body and set the MIME type to text/html
    yag.send(to=recipient, subject=subject, contents=contents)
