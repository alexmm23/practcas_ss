from flask import Flask, render_template, request, redirect, session, url_for
import pyotp
import datetime
import io
import base64
import qrcode
app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Usuario simulado
USER = {
    "username": "admin",
    "password": "1234",
    "totp_secret": "JBSWY3DPEHPK3PXP"  # Clave secreta para TOT
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USER['username'] and request.form['password'] == USER['password']:
            session['user'] = USER['username']
            return redirect(url_for('mfa'))
    return render_template('login.html')

@app.route('/mfa', methods=['GET', 'POST'])
def mfa():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Imprimir hora de servidor python
        print("Hora de servidor:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # Imprimir hora de Google Authenticator
        print("Hora de Google Authenticator:", request.form['token'])
        totp = pyotp.TOTP(USER['totp_secret']) 
        print(totp.secret)
        print("Token recibido:", request.form['token'])
        print(USER['totp_secret'])
        print(totp.now())
        print(totp.verify(request.form['token']))

        token = request.form['token'].strip()
        print("Token limpio:", token)
        print("TOTP generado:", totp.now())
        print("Verificación:", totp.verify(token, valid_window=2))

        if totp.verify(token, valid_window=2):
            session['mfa'] = True
            return f"<h2>Bienvenido {session['user']}, autenticación exitosa.</h2>"
        else:
            return "<h2>Código incorrecto. Intenta de nuevo.</h2>"

    return render_template('mfa.html')

@app.route('/qr')
def qr():
    totp = pyotp.TOTP(USER['totp_secret'])
    uri = totp.provisioning_uri(name="admin@demo", issuer_name="LoginMFA")
    # Generar QR en memoria
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    # Mostrar QR en HTML
    return f"""
    <p>Agrega esta URL en Google Authenticator:<br><code>{uri}</code></p>
    <p>O escanea este código QR:</p>
    <img src="data:image/png;base64,{img_b64}" alt="QR Code">
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
