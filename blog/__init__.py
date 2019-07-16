import os
import click

from flask import Flask, render_template
from blog.settings import config
from blog.blueprints.auth import auth
from blog.blueprints.admin import admin
from blog.blueprints.blog import blog
from blog.models import Admin, Category, Comment, Link

from flask_login import current_user

from blog.extensions import bootstrap, db, moment, ckeditor, mail, login_manager, csrf
from flask_wtf.csrf import CSRFError


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
    register_tempalate_context(app)

    return app


def register_logging(app):
    pass


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)


def register_blueprints(app):
    app.register_blueprint(blog)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(auth, url_prefix='/auth')


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


def register_tempalate_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(admin=admin, categories=categories, unread_comments=unread_comments, links=links)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def bad_request(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def bad_request(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def bad_request(e):
        return render_template('errors/400.html', description=e.description), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop')
    def initdb(drop):
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables')
        db.create_all()
        click.echo('Initialized database')

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, help='The password used to login.')
    def init(username, password):
        click.echo('Initializing thme database...')
        db.create_all()

        admin = Admin.query.first()

        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)

        else:
            click.echo('Create the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title='天涯若比邻',
                blog_sub_title='No, I`am the real thing.',
                name='Admin',
                about='Anything about you.'
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')

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
