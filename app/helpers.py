import os
from flask import current_app as app, jsonify
from werkzeug.utils import secure_filename
from PIL import Image


def upload_img(file, prefix, type='thumbnail'):
    filename = secure_filename(file.filename)
    if filename != '':
        extension = filename.split(".")[-1]
        if prefix and type:
            name = prefix + f'_{type}.' + extension
            name_min = prefix + f'_{type}_min.' + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER_ABS'], f'{type}s', name))
            save_resized_image(file, type, name_min)
            return name, name_min
        else:
            return False


def delete_img(filename, type='thumbnails'):
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER_ABS'], f'{type}', filename)):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER_ABS'], f'{type}', filename))
        return True
    else:
        return False


def upload_success(url: str):
    data = {
        'url': url
    }
    return jsonify(data)


def upload_fail(message: str):
    data = {
        'error': {
            'message': message
        }
    }
    return jsonify(data)


def save_resized_image(file, type, name):
    size = 320, 180
    try:
        im = Image.open(file)
        im.thumbnail(size, Image.Resampling.LANCZOS)
        im.save(os.path.join(app.config['UPLOAD_FOLDER_ABS'], f'{type}s', name))
    except IOError:
        print("Can't create minified version of the image!")
