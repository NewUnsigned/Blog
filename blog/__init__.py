import os
from flask import Flask
from blog.settings import config
from blog.blueprints.auth import auth
from blog.blueprints.admin import admin
from blog.blueprints.blog import blog

from blog.extensions import bootstrap, db, moment, ckeditor, mail


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('blog')
    app.config.from_object(config[config_name])
    app.register_blueprint(blog)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(auth, url_prefix='/auth')

    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)

    return app

# 端点：使用端点可以实现蓝本的视图函数命名空间
# app.add_url_rule('/hello', 'say_heelo', say_hello)
