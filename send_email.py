import imaplib
import email
from email.header import decode_header

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('alrivera86@gmail.com', 'ojpppwgsubiikuyw')
mail.select('inbox')

status, messages = mail.search(None, 'ALL')
ids = messages[0].split()
last3 = ids[-3:]

for uid in reversed(last3):
    res, msg_data = mail.fetch(uid, '(RFC822)')
    msg = email.message_from_bytes(msg_data[0][1])
    
    subj_raw, enc = decode_header(msg['Subject'])[0]
    subject = subj_raw.decode(enc or 'utf-8') if isinstance(subj_raw, bytes) else subj_raw
    sender = msg['From']
    date = msg['Date']
    
    print(f"--- Correo #{uid.decode()} ---")
    print(f"De:    {sender}")
    print(f"Asunto: {subject}")
    print(f"Fecha:  {date}")
    print()

mail.logout()