import os
import shutil

from werkzeug.utils import secure_filename
from PIL import Image
from backend.src.utils.exceptions import UserError
from backend.src.utils.constants import ALLOWED_IMG_EXTENSIONS, UPLOAD_FOLDER, IMAGE_PATHS
from .exceptions import ConfigurationError

import logging

logger = logging.getLogger('backend')


def is_allowed_file(filename):
    """
    Check if file type is in allowed extensions list.
    Used for image upload validation.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMG_EXTENSIONS


def validate_image(file):
    """
    Validate uploaded image file.

    Checks:
    - File presence
    - Valid extension (PNG, JPG, JPEG)
    - Maximum file size from config
    - Image file integrity
    """
    # getting config env var
    from flask import current_app
    img_max_size = current_app.config["MAX_FILE_SIZE"]

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


def save_image_from_request(file, entity_name, slug):
    """
    Save uploaded image for venue or event.

    - Creates directory if not exists
    - Processes image with PIL
    - Resizes to standard width while maintaining aspect ratio
    """
    img_dir = os.path.join(UPLOAD_FOLDER, 'img', entity_name, slug)
    os.makedirs(img_dir, exist_ok=True)

    filename = secure_filename(f"{slug}.png")
    file_path = os.path.join(img_dir, filename)

    img = Image.open(file)
    img = img.convert('RGBA')

    # getting current size
    width, height = img.size
    # new width and height to fit our proportions
    new_width = 400
    new_height = int((height / width) * new_width)
    # saving new size with good quality
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    img.save(file_path, 'PNG')
    logger.info(f"Saved image for {entity_name}: {file_path}")

    return IMAGE_PATHS[entity_name].format(slug=slug, filename=filename)


def delete_folder_from_path(image_path):
    """
    Delete folder that contains the image based on image path.

    Example: for '/uploads/img/venues/haifa-museum/image.png'
    deletes the 'haifa-museum' folder with all contents.

    Skips deletion if folder is 'default'.
    """
    relative_path = image_path.replace('/uploads/', '', 1)
    full_path = os.path.join(UPLOAD_FOLDER, relative_path)
    folder_to_delete = os.path.dirname(full_path)

    if os.path.basename(folder_to_delete) == 'default':
        return

    if os.path.exists(folder_to_delete):
        shutil.rmtree(folder_to_delete)
        logger.info(f"Deleted folder: {folder_to_delete}")


def rename_image_folder(entity_name, old_slug, new_slug):
    """
    Rename image folder when entity's slug changes.

    Example: when venue's slug changes from 'old-cafe' to 'new-cafe',
    renames '/uploads/img/venues/old-cafe' to '/uploads/img/venues/new-cafe'

    Returns new image path or constructs path for non-existent folder.
    """
    old_dir = os.path.join(UPLOAD_FOLDER, 'img', entity_name, old_slug)
    new_dir = os.path.join(UPLOAD_FOLDER, 'img', entity_name, new_slug)

    # If folder doesn't exist (e.g. using default image) - skip
    if not os.path.exists(old_dir):
        return IMAGE_PATHS[entity_name].format(
            slug=new_slug,
            filename=f"{new_slug}.png"
        )

    try:
        # Rename folder
        os.rename(old_dir, new_dir)

        # Rename image file inside
        old_file = os.path.join(new_dir, f"{old_slug}.png")
        new_file = os.path.join(new_dir, f"{new_slug}.png")

        if os.path.exists(old_file):
            os.rename(old_file, new_file)

        logger.info(f"Renamed folder from {old_dir} to {new_dir}")

        return IMAGE_PATHS[entity_name].format(
            slug=new_slug,
            filename=f"{new_slug}.png"
        )

    except Exception as e:
        raise ConfigurationError(f"Failed to rename image folder: {str(e)}")
