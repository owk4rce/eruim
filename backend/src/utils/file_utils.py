import os
from werkzeug.utils import secure_filename
from PIL import Image
from flask import current_app
from backend.src.utils.exceptions import UserError
from backend.src.utils.constants import ALLOWED_IMG_EXTENSIONS, UPLOAD_FOLDER
from .exceptions import ConfigurationError


def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMG_EXTENSIONS


def validate_image(file):
    img_max_size = os.getenv("MAX_FILE_SIZE")

    if not img_max_size:
        raise ConfigurationError("MAX_FILE_SIZE not set in .env")

    if not file:
        raise UserError("No file uploaded.")

    if not is_allowed_file(file.filename):
        raise UserError(f"Invalid file type. Allowed: {', '.join(ALLOWED_IMG_EXTENSIONS)}")

    # counting size of file - move pointer to the end and get position in bytes
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    img_max_size = int(img_max_size)

    if size > img_max_size:
        raise UserError(f"File too large. Max: {img_max_size // (1024 * 1024)}MB")

    try:
        img = Image.open(file)
        img.verify()
        file.seek(0)
    except Exception:
        raise UserError("Invalid image file")


def save_venue_image(file, venue_slug):
    venue_dir = os.path.join(UPLOAD_FOLDER, 'img', 'venues', venue_slug)
    os.makedirs(venue_dir, exist_ok=True)

    filename = secure_filename(f"{venue_slug}.png")
    file_path = os.path.join(venue_dir, filename)

    img = Image.open(file)
    img = img.convert('RGBA')
    img = img.resize((400, 400))
    img.save(file_path, 'PNG')

    return f"/uploads/img/venues/{venue_slug}/{filename}"
