import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

msg = MIMEMultipart()
msg['Subject'] = 'CTF GitOps Chile 2026 - Resultado y Flag'
msg['From'] = 'alrivera86@gmail.com'
msg['To'] = 'dalcaino@bancochile.cl'

body = '''Hola Daniel,

Te comparto el resultado del desafio CTF GitOps Chile 2026.

FLAG OBTENIDA:
flag{p4r4m_1nj3ct10n_g1t_cl0n3_h00k_2024}

WRITEUP COMPLETO:
https://github.com/alrivera86/ctf-gitops-writeup

TECNICA UTILIZADA:
Parameter injection en git clone mediante:
  --config url.X.insteadOf  (URL rewriting al repo del atacante)
  --config filter.run.smudge=sh  (smudge filter RCE)

El pipeline ejecutaba: git clone https://github.com/pelicancorp/SERVICE_NAME.git
Se inyecto SERVICE_NAME con flags de git que redirigen el clone a un repo controlado
y ejecutan sh sobre los archivos al hacer checkout, corriendo cat /flag.txt.

Saludos,
Alberto Rivera
'''

msg.attach(MIMEText(body, 'plain'))
with smtplib.SMTP('smtp.gmail.com', 587) as s:
    s.starttls()
    s.login('alrivera86@gmail.com', 'ojpppwgsubiikuyw')
    s.send_message(msg)
print('Correo enviado exitosamente!')