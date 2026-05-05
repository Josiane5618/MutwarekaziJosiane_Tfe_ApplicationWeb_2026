from app.utils import email_service


def test_send_email_uses_preview_when_smtp_is_disabled(monkeypatch, capsys):
    monkeypatch.setattr(email_service, "SMTP_ENABLED", False)

    sent = email_service.send_email(
        "josiane@example.com",
        "Inscription acceptée",
        "Votre compte a été validé."
    )

    output = capsys.readouterr().out

    assert sent is False
    assert "EMAIL SIMULE" in output
    assert "josiane@example.com" in output
    assert "Inscription acceptée" in output


def test_send_email_uses_smtp_when_enabled(monkeypatch):
    sent_messages = []

    class FakeSmtp:
        def __init__(self, host, port, timeout):
            self.host = host
            self.port = port
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def send_message(self, message):
            sent_messages.append(message)

    monkeypatch.setattr(email_service, "SMTP_ENABLED", True)
    monkeypatch.setattr(email_service, "SMTP_HOST", "127.0.0.1")
    monkeypatch.setattr(email_service, "SMTP_PORT", 1025)
    monkeypatch.setattr(email_service, "SMTP_USERNAME", "")
    monkeypatch.setattr(email_service, "SMTP_USE_TLS", False)
    monkeypatch.setattr(email_service.smtplib, "SMTP", FakeSmtp)

    sent = email_service.send_email(
        "josiane@example.com",
        "Inscription acceptée",
        "Votre compte a été validé."
    )

    assert sent is True
    assert len(sent_messages) == 1
    assert sent_messages[0]["To"] == "josiane@example.com"
    assert sent_messages[0]["Subject"] == "Inscription acceptée"
