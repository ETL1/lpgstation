
import io
import qrcode
from django.core.files.base import ContentFile

def make_qr_png(data: str):
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return ContentFile(buf.getvalue(), name='qr.png')
