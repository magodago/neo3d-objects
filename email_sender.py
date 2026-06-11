#!/usr/bin/env python3
"""
NEO Objects — Email Sender
Envía emails personalizados con el catálogo a tiendas potenciales.
Soporta tres modos: Gmail API, SMTP directo, o archivo para MailerLite.
"""
import smtplib, ssl, json, csv, os, time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime
from email_campaign import generate_all_emails

BASE_DIR = Path.home() / "gema_store" / "neo3d"

# ─── Config SMTP (para cuando tengamos credenciales) ───
SMTP_CONFIG = {
    "gmail": {
        "host": "smtp.gmail.com",
        "port": 587,
        "use_tls": True,
    },
}

def send_email_smtp(smtp_host, smtp_port, username, password, to_email, subject, body,
                    pdf_path=None, use_tls=True):
    """Send an email via SMTP."""
    msg = MIMEMultipart("alternative")
    msg["From"] = username
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Reply-To"] = username
    
    # Plain text body
    msg.attach(MIMEText(body, "plain", "utf-8"))
    
    # Attach PDF catalog if exists
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="catalogo_neo_objects.pdf"',
            )
            msg.attach(part)
    
    # Send
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if use_tls:
            server.starttls(context=context)
        server.login(username, password)
        server.sendmail(username, to_email, msg.as_string())
    
    return True


def send_batch(stores_list, email_user, email_pass, smtp_provider="gmail",
               max_per_hour=20, catalog_pdf=None, dry_run=True):
    """
    Send emails in batch with rate limiting.
    dry_run=True: just print what would be sent.
    dry_run=False: actually send.
    """
    config = SMTP_CONFIG.get(smtp_provider)
    if not config:
        print(f"❌ SMTP provider '{smtp_provider}' not configured")
        return
    
    emails = generate_all_emails()
    if not emails:
        # Filter stores list
        emails = []
        for s in stores_list:
            if s.get("email"):
                from email_campaign import generate_email
                emails.append(generate_email(s))
    
    print(f"\n{'=' * 50}")
    print(f"  📧 ENVIANDO EMAILS")
    print(f"  Modo: {'🔍 SIMULACIÓN (dry-run)' if dry_run else '🚀 EN VIVO'}")
    print(f"  Total a enviar: {len(emails)}")
    print(f"  Límite: {max_per_hour}/hora")
    print(f"{'=' * 50}\n")
    
    sent = 0
    failed = 0
    
    for i, e in enumerate(emails, 1):
        print(f"[{i}/{len(emails)}] {e['to_name']} <{e['to_email']}>")
        print(f"       Asunto: {e['subject']}")
        
        if not dry_run:
            try:
                send_email_smtp(
                    config["host"], config["port"],
                    email_user, email_pass,
                    e["to_email"], e["subject"], e["body"],
                    pdf_path=catalog_pdf,
                    use_tls=config["use_tls"],
                )
                print(f"       ✅ Enviado")
                sent += 1
            except Exception as ex:
                print(f"       ❌ Error: {ex}")
                failed += 1
            
            # Rate limit: 20 emails/hour → 1 cada 3 minutos
            if i < len(emails):
                wait = 180  # 3 min
                print(f"       ⏳ Esperando {wait}s...")
                time.sleep(wait)
        else:
            print(f"       📝 (simulado)")
            sent += 1
    
    print(f"\n{'=' * 50}")
    print(f"  📊 RESULTADOS")
    print(f"  Enviados: {sent}")
    print(f"  Fallos: {failed}")
    print(f"{'=' * 50}")
    
    # Save log
    log = {
        "date": datetime.now().isoformat(),
        "total": len(emails),
        "sent": sent,
        "failed": failed,
        "dry_run": dry_run,
        "emails": [{"to": e["to_email"], "name": e["to_name"], "subject": e["subject"]} for e in emails],
    }
    log_path = BASE_DIR / f"email_campaign_log_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"📄 Log guardado: {log_path}")


if __name__ == "__main__":
    import sys
    
    dry_run = "--send" not in sys.argv
    
    if "--mailerlite" in sys.argv:
        # Just prepare MailerLite import
        emails = generate_all_emails()
        path = Path(BASE_DIR) / "mailerlite_import.csv"
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(["email", "name", "city", "store_type"])
            for e in emails:
                w.writerow([e['to_email'], e['to_name'], e['store_city'], e['store_category']])
        print(f"✅ MailerLite import CSV: {path} ({len(emails)} contacts)")
    else:
        send_batch([], None, None, dry_run=dry_run)
