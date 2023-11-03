from flask import Flask, render_template, jsonify
import subprocess
import json
import qrcode
import serial
from PIL import Image
from nostr_publish import * 
import threading

invoice = None
app = Flask(__name__)

@app.route('/')
def index(): 
    r_hash, payment_request = create_private_invoice()
    img_qr = generate_qr(payment_request)
    return render_template('index2.html', qr_code=img_qr, r_hash=r_hash)

@app.route('/check_invoice/<r_hash>')
def check_invoice(r_hash):
    global invoice
    status = check_invoice_status(r_hash)
    if status == 'SETTLED':
        send_data_to_serial("/dev/ttyUSB0", b'1')
        if invoice != None:
            t = threading.Thread(target=Publish_in_nostr, args=(invoice,))
            t.start()    
        print('Acionou o arduino')
    return jsonify({'status': status})

def create_private_invoice():
    cmd = ['lncli', 'addinvoice', '--amt=6000', '--private']
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return data['r_hash'], data['payment_request']

def check_invoice_status(r_hash):
    global invoice
    cmd = ['lncli', 'lookupinvoice', r_hash]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    invoice = data['payment_request']
    return data['state']

def send_data_to_serial(port, data, baudrate=115200):
    with serial.Serial(port, baudrate) as ser:
        ser.write(data)

def generate_qr(payment_request, size=150):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data(payment_request)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    img_qr.save('static/qr.png')
    return 'static/qr.png'

if __name__ == "__main__":
    app.run(debug=True, port=8000)
