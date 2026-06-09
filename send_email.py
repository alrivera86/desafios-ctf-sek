import imaplib
import email
from email.header import decode_header

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('alrivera86@gmail.com', 'ojpppwgsubiikuyw')
mail.select('inbox')

# Use SORT or just fetch by recent sequence numbers
status, data = mail.select('inbox')
total = int(data[0])
print(f"Total mensajes en inbox: {total}")

# Fetch last 3 by sequence number
for seq in range(total, total-3, -1):
    res, msg_data = mail.fetch(str(seq), '(RFC822.HEADER)')
    if msg_data and msg_data[0]:
        msg = email.message_from_bytes(msg_data[0][1])
        
        raw_subj = msg['Subject'] or '(sin asunto)'
        subj_parts = decode_header(raw_subj)
        subject = ''
        for part, enc in subj_parts:
            if isinstance(part, bytes):
                subject += part.decode(enc or 'utf-8', errors='replace')
            else:
                subject += part
        
        sender = msg['From'] or '?'
        date = msg['Date'] or '?'
        
        print(f"\n--- Correo #{seq} ---")
        print(f"De:     {sender[:80]}")
        print(f"Asunto: {subject[:100]}")
        print(f"Fecha:  {date}")

mail.logout()