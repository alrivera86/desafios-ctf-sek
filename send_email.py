import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

msg = MIMEMultipart()
msg['Subject'] = 'CTF GitOps Chile 2026 - Resultado y Flag'
msg['From'] = 'alrivera86@gmail.com'
msg['To'] = 'ariverar@bancochile.cl'

body = '''Hola Alberto,

Te comparto el resultado del desafio CTF GitOps Chile 2026.

FLAG OBTENIDA:
flag{p4r4m_1nj3ct10n_g1t_cl0n3_h00k_2024}

WRITEUP COMPLETO:
https://github.com/alrivera86/ctf-gitops-writeup

TECNICA UTILIZADA:
Parameter injection en git clone mediante:
  --config url.X.insteadOf  (URL rewriting al repo del atacante)
  --config filter.run.smudge=sh  (smudge filter RCE)

Saludos,
Alberto Rivera
'''

msg.attach(MIMEText(body, 'plain'))

# Attach the docx file
with open('attachment.docx', 'rb') as f:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="Prueba bines externo (1) 1.docx"')
    msg.attach(part)

with smtplib.SMTP('smtp.gmail.com', 587) as s:
    s.starttls()
    s.login('alrivera86@gmail.com', 'ojpppwgsubiikuyw')
    s.send_message(msg)
print('Correo con adjunto enviado exitosamente!')