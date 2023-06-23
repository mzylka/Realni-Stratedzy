import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    APP_MAIL_SUBJECT_PREFIX = '[Realni Stratedzy]'
    APP_MAIL_SENDER = 'Realni Stratedzy'
    APP_ADMIN = os.environ.get('APP_ADMIN')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_SALT = os.environ.get('SECRET_KEY')

    FLASKY_POSTS_PER_PAGE = 20

    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_PKG_TYPE = "standard"
    CKEDITOR_FILE_UPLOADER = 'upload_cke'
    UPLOAD_FOLDER_ABS = os.path.join(basedir, 'files')
    UPLOAD_FOLDER = 'files'
    ALLOWED_EXTENSIONS = {'jpg', 'png'}

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False
    APP_ADMIN = "admin@test.com"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
