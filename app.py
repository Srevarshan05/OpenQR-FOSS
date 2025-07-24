from flask import Flask, request, jsonify, send_file
import qrcode
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image

app = Flask(__name__)

@app.route('/')
def index():
    return open('index.html').read()

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Generate QR code
    qr = qrcode.make(url)
    
    # Save to BytesIO buffer as PNG for display
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Convert to base64 for frontend display
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    qr_image = f'data:image/png;base64,{qr_base64}'
    
    return jsonify({'qr_image': qr_image})

@app.route('/download_qr', methods=['POST'])
def download_qr():
    data = request.get_json()
    url = data.get('url')
    format = data.get('format', 'png').lower()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Generate QR code
    qr = qrcode.make(url)
    
    buffer = BytesIO()
    
    if format == 'png':
        qr.save(buffer, format='PNG')
        mime_type = 'image/png'
        filename = 'qr_code.png'
    elif format == 'jpg':
        qr.save(buffer, format='PNG')  # Save as PNG first
        img = Image.open(buffer).convert('RGB')
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        mime_type = 'image/jpeg'
        filename = 'qr_code.jpg'
    elif format == 'pdf':
        c = canvas.Canvas(buffer, pagesize=letter)
        img_buffer = BytesIO()
        qr.save(img_buffer, format='PNG')
        img = Image.open(img_buffer)
        img_width, img_height = img.size
        c.drawImage(img_buffer, (letter[0] - img_width) / 2, (letter[1] - img_height) / 2, img_width, img_height)
        c.showPage()
        c.save()
        mime_type = 'application/pdf'
        filename = 'qr_code.pdf'
    else:
        return jsonify({'error': 'Unsupported format'}), 400
    
    buffer.seek(0)
    return send_file(buffer, mimetype=mime_type, as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=False)