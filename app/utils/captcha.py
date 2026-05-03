"""Captcha generation utility using Pillow."""

import random
import string
import uuid
from io import BytesIO
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

_captcha_store = {}

def generate_captcha_text(length: int = 6) -> str:
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
    return ''.join(random.choices(chars, k=length))

def generate_captcha_image(text: str) -> bytes:
    width, height = 200, 80
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Background noise
    for _ in range(150):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r, g, b = random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)
        draw.point((x, y), fill=(r, g, b))

    # Try to load a font, fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 36)
        except:
            font = ImageFont.load_default()

    # Draw text with slight random offsets
    x_offset = 20
    for char in text:
        y_offset = random.randint(-5, 5)
        r = random.randint(50, 120)
        g = random.randint(50, 120)
        b = random.randint(50, 120)
        draw.text((x_offset, 25 + y_offset), char, font=font, fill=(r, g, b))
        x_offset += 30

    # Add distortion lines
    for _ in range(3):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill=(100, 100, 100), width=2)

    # Save to bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()

def create_captcha(expiry_minutes: int = 5) -> dict:
    captcha_id = str(uuid.uuid4())
    answer = generate_captcha_text()
    image_bytes = generate_captcha_image(answer)
    expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    
    _captcha_store[captcha_id] = {
        "answer": answer,
        "expires_at": expires_at
    }
    
    return {
        "captcha_id": captcha_id,
        "image": image_bytes,
        "expires_at": expires_at.isoformat()
    }

def verify_captcha(captcha_id: str, answer: str) -> bool:
    if captcha_id not in _captcha_store:
        return False
    
    captcha = _captcha_store[captcha_id]
    if datetime.utcnow() > captcha["expires_at"]:
        del _captcha_store[captcha_id]
        return False
    
    correct = captcha["answer"].upper() == answer.upper()
    del _captcha_store[captcha_id]  # One-time use
    return correct

def cleanup_expired_captchas():
    now = datetime.utcnow()
    expired = [k for k, v in _captcha_store.items() if now > v["expires_at"]]
    for k in expired:
        del _captcha_store[k]
