from flask import Flask, render_template, request, redirect, session, url_for
import pyotp

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Usuario simulado
USER = {
    "username": "admin",
    "password": "1234",
    "totp_secret": pyotp.random_base32()  # cámbialo si quieres hacerlo fijo
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
        totp = pyotp.TOTP(USER['totp_secret'])
        if totp.verify(request.form['token']):
            return f"<h2>Bienvenido {session['user']}, autenticación exitosa.</h2>"
        else:
            return "<h2>Código incorrecto. Intenta de nuevo.</h2>"

    return render_template('mfa.html')

@app.route('/qr')
def qr():
    totp = pyotp.TOTP(USER['totp_secret'])
    uri = totp.provisioning_uri(name="admin@demo", issuer_name="LoginMFA")
    return f"<p>Agrega esta URL en Google Authenticator:<br><code>{uri}</code></p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
