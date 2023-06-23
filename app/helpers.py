import os
from werkzeug.utils import secure_filename


def upload_img(file, prefix, type='thumbnail'):
    filename = secure_filename(file.filename)
    if filename != '':
        extension = filename.split(".")[-1]
        if prefix and type:
            name = prefix + f'_{type}.' + extension
            file.save(os.path.join(f'files/{type}s', name))
            return name
        else:
            return False
