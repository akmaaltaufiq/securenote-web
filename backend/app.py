from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask import send_from_directory
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import os

app = Flask(__name__)
CORS(app)

# Folder penyimpanan file terenkripsi dan key
EMAIL_FOLDER = os.path.join(os.path.dirname(__file__), "emails")
os.makedirs(EMAIL_FOLDER, exist_ok=True)

KEYS_FOLDER = os.path.join(os.path.dirname(__file__), "keys")
os.makedirs(KEYS_FOLDER, exist_ok=True)

# Load atau generate RSA key
def load_or_generate_rsa_keys():
    private_key_path = os.path.join(KEYS_FOLDER, "private_key.pem")
    public_key_path = os.path.join(KEYS_FOLDER, "public_key.pem")

    if os.path.exists(private_key_path) and os.path.exists(public_key_path):
        with open(private_key_path, "rb") as f:
            private_key = f.read()
        with open(public_key_path, "rb") as f:
            public_key = f.read()
        print("[INFO] RSA keys loaded.")
    else:
        print("[INFO] Generating new RSA keys...")
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()

        with open(private_key_path, "wb") as f:
            f.write(private_key)
        with open(public_key_path, "wb") as f:
            f.write(public_key)
        print("[INFO] RSA keys generated and saved.")

    return private_key, public_key

private_key, public_key = load_or_generate_rsa_keys()

# AES Encrypt
def aes_encrypt(message, aes_key):
    cipher = AES.new(aes_key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    return cipher.iv, ct_bytes

# AES Decrypt
def aes_decrypt(iv, ciphertext, aes_key):
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), AES.block_size)

# RSA Encrypt AES key
def rsa_encrypt_key(aes_key, public_key):
    rsa_key = RSA.import_key(public_key)
    cipher_rsa = PKCS1_OAEP.new(rsa_key)
    return cipher_rsa.encrypt(aes_key)

# RSA Decrypt AES key
def rsa_decrypt_key(enc_key, private_key):
    rsa_key = RSA.import_key(private_key)
    cipher_rsa = PKCS1_OAEP.new(rsa_key)
    return cipher_rsa.decrypt(enc_key)

# Endpoint untuk enkripsi email
@app.route("/encrypt", methods=["POST"])
def encrypt_email():
    data = request.get_json()
    subject = data.get("subject", "")
    message = data.get("message", "")

    aes_key = get_random_bytes(16)
    iv, encrypted_message = aes_encrypt(message, aes_key)
    enc_aes_key = rsa_encrypt_key(aes_key, public_key)

    # Encode ke base64
    enc_message_b64 = base64.b64encode(encrypted_message).decode()
    enc_key_b64 = base64.b64encode(enc_aes_key).decode()
    iv_b64 = base64.b64encode(iv).decode()

    # Simpan ke file
    filename = f"email_{subject.replace(' ', '_')}.txt"
    filepath = os.path.join(EMAIL_FOLDER, filename)
    with open(filepath, "w") as f:
        f.write(f"Subject: {subject}\n")
        f.write(f"Encrypted Message: {enc_message_b64}\n")
        f.write(f"Encrypted AES Key: {enc_key_b64}\n")
        f.write(f"AES IV: {iv_b64}\n")

    return jsonify({
        "subject": subject,
        "encrypted_message": enc_message_b64,
        "enc_aes_key": enc_key_b64,
        "iv": iv_b64,
        "filename": filename
    })

# Endpoint untuk dekripsi email
@app.route("/decrypt", methods=["POST"])
def decrypt_email():
    file = request.files["file"]
    lines = file.read().decode().splitlines()

    if len(lines) < 4:
        return jsonify({"error": "Invalid file format"}), 400

    try:
        subject = lines[0].split(": ", 1)[1]
        enc_message = base64.b64decode(lines[1].split(": ", 1)[1])
        enc_aes_key = base64.b64decode(lines[2].split(": ", 1)[1])
        iv = base64.b64decode(lines[3].split(": ", 1)[1])

        aes_key = rsa_decrypt_key(enc_aes_key, private_key)
        decrypted_message = aes_decrypt(iv, enc_message, aes_key).decode()

        return jsonify({
            "subject": subject,
            "message": decrypted_message
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint untuk download file hasil enkripsi
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(EMAIL_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
