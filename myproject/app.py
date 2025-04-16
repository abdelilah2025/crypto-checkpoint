from flask import Flask, render_template, request
import gnupg
import os

app = Flask(__name__)

# Crée le répertoire gnupg_home s'il n'existe pas
gnupg_home = './gnupg_home'
if not os.path.exists(gnupg_home):
    os.makedirs(gnupg_home)

gpg = gnupg.GPG(gnupghome=gnupg_home)  # Clés stockées ici

# Crée une clé la première fois (si aucune n'existe)
def setup_key():
    keys = gpg.list_keys(True)  # Clés privées
    if not keys:
        input_data = gpg.gen_key_input(
            name_email='user@example.com',
            passphrase='pass'
        )
        gpg.gen_key(input_data)

setup_key()

@app.route("/", methods=["GET", "POST"])
def index():
    original_text = ""
    encrypted_text = ""
    decrypted_text = ""
    signature = ""

    if request.method == "POST":
        action = request.form.get("action")
        original_text = request.form.get("original_text", "")
        encrypted_input = request.form.get("encrypted_text", "")

        private_keys = gpg.list_keys(True)
        fingerprint = private_keys[0]['fingerprint'] if private_keys else None

        if action == "encrypt" and fingerprint:
            encrypted_data = gpg.encrypt(original_text, recipients=[fingerprint], always_trust=True)
            encrypted_text = str(encrypted_data)

            signed_data = gpg.sign(original_text, keyid=fingerprint, passphrase="pass")
            signature = str(signed_data)

        elif action == "decrypt":
            decrypted_data = gpg.decrypt(encrypted_input, passphrase="pass")
            decrypted_text = str(decrypted_data)

    return render_template("index.html",
                           original_text=original_text,
                           encrypted_text=encrypted_text,
                           decrypted_text=decrypted_text,
                           signature=signature)

if __name__ == "__main__":
   app.run(debug=True, host='0.0.0.0', port=8001)
