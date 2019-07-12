from flask import Blueprint

admin = Blueprint('admin', __name__)


@admin.route('/new_post')
def new_post():
    print('new_post')


@admin.route('/new_category')
def new_category():
    print('new_category')


@admin.route('/new_link')
def new_link():
    print('new_link')


@admin.route('/manage_post')
def manage_post():
    print('manage_post')


@admin.route('/manage_category')
def manage_category():
    print('manage_category')


@admin.route('/manage_link')
def manage_link():
    print('manage_link')


@admin.route('/manage_comment')
def manage_comment():
    print('manage_comment')


@admin.route('/settings')
def settings():
    print('settings')
