import os
import click

from flask import Flask, render_template
from blog.settings import config
from blog.blueprints.auth import auth
from blog.blueprints.admin import admin
from blog.blueprints.blog import blog

from blog.extensions import bootstrap, db, moment, ckeditor, mail


# 程序入口
def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('blog')
    app.config.from_object(config[config_name])

    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_errors(app)
    register_commands(app)
    register_shell_context(app)
    register_tempalte_context(app)

    return app


def register_logging(app):
    pass


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)


def register_blueprints(app):
    app.register_blueprint(blog)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(auth, url_prefix='/auth')


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


def register_tempalte_context(app):
    pass


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories')
    @click.option('--post', default=50, help='Quantity of posts')
    @click.option('--comment', default=500, help='Quantity of comments')
    def forge(category, post, comment):
        from blog.fakes import fake_admin, fake_categories, fake_comments, fake_posts

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Generating %d comments' % comment)
        fake_comments(comment)

        click.echo('Done')

# 端点：使用端点可以实现蓝本的视图函数命名空间
# app.add_url_rule('/hello', 'say_heelo', say_hello)
