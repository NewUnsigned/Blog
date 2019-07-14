from flask import Blueprint, render_template, request, current_app
from flask_login import login_required
from blog.models import Post

admin = Blueprint('admin', __name__)


@admin.before_request
@login_required
def login_protect():
    pass


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
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_MANAGE_POST_PER_PAGE']
    )
    posts = pagination.items
    return render_template('admin/manage_post.html', pagination=pagination, posts=posts, page=page)


@admin.route('/delete_post', methods=['POST'])
def delete_post(post_id=None, next=None):
    print('delete_post')


@admin.route('/edit_post')
def edit_post():
    print('edit_post')


@admin.route('/set_comment')
def set_comment():
    print('set_comment')


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
    return render_template('/admin/settings.html')
