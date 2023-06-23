import os
from flask import Flask, send_from_directory, request, url_for
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_ckeditor import CKEditor, upload_success, upload_fail

mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
ckeditor = CKEditor()

login_manager = LoginManager()
login_manager.login_view = 'control_panel.auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)
    ckeditor.init_app(app)

    login_manager.init_app(app)

    def allowed_file(filename):
        return '.' in filename and filename.split('.')[-1].lower() in {'jpg', 'gif', 'png', 'jpeg'}

    @app.route('/files/<path:folder>/<path:filename>')
    def uploaded_files(folder, filename):
        path = os.path.join(app.config['UPLOAD_FOLDER_ABS'], folder)
        return send_from_directory(path, filename)

    @app.route('/upload-cke', methods=['GET', 'POST'])
    def upload_cke():
        f = request.files.get('upload')
        upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'cke_images')
        if f.filename in os.listdir(upload_folder):
            return upload_fail(message="The image with the same name already exists on the server! Please change the name of the image!")
        if not allowed_file(f.filename):
            return upload_fail(message='Image Only!')
        f.save(os.path.join(upload_folder, f.filename))
        url = url_for('uploaded_files', folder='cke_images', filename=f.filename)
        return upload_success(url, filename=f.filename)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .control_panel import control_panel as control_panel_blueprint
    app.register_blueprint(control_panel_blueprint, url_prefix='/control-panel')

    return app
