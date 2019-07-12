from flask import Blueprint, render_template, request, current_app

from blog.models import Post

blog = Blueprint('blog', __name__)


@blog.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/index.html', posts=posts, pagination=pagination)


@blog.route('/about')
def about():
    return render_template('blog/about.html')


@blog.route('/category/<int:category_id>')
def show_category(category_id):
    return render_template('blog/category.html')


@blog.route('/post/<int:post_id>')
def show_post():
    return render_template('/blog/post.html')
