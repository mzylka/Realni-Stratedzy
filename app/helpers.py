import os
from flask import current_app as app
from werkzeug.utils import secure_filename


def upload_img(file, prefix, type='thumbnail'):
    filename = secure_filename(file.filename)
    if filename != '':
        extension = filename.split(".")[-1]
        if prefix and type:
            name = prefix + f'_{type}.' + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER_ABS'], f'{type}s', name))
            return name
        else:
            return False


def delete_img(filename, type='thumbnail'):
    if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER_ABS'], f'{type}s', filename)):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER_ABS'], f'{type}s', filename))
        return True
    else:
        return False
