from flask import current_app
import secrets
import os
from PIL import Image


def allowed_files(filename, allowd_exts):
    try:
        is_dot_in_filename = '.' in filename
        if_ext_in_allowed_exts = filename.rsplit(
            '.', 1)[1].lower() in allowd_exts

        return if_ext_in_allowed_exts and is_dot_in_filename
    except Exception:
        return False


def save_hkthon_imgs(file):
    random_hex = secrets.token_hex(8)
    _, ext = os.path.splitext(file.filename)
    picture_fn = random_hex + ext
    picture_path = os.path.join(
        current_app.config['UPLOAD_FOLDER'], 'hakthon_imgs', picture_fn)
    output_size = (200, 200)
    new_file = Image.open(file)
    new_file.thumbnail(output_size)
    new_file.save(picture_path)

    return picture_fn
