from flask import Blueprint, render_template, request, current_app, url_for, flash, redirect, abort, make_response

from blog.models import Post, Comment, Category
from blog.forms import AdminCommentForm, CommentForm
from flask_login import current_user
from blog.utils import redirect_back

from blog.extensions import db

blog = Blueprint('blog', __name__)


@blog.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    return render_template('blog/index.html', posts=posts, pagination=pagination)


@blog.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=1)
    per_page = current_app.config['BLOG_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.desc()).paginate(
        page, per_page
    )
    comments = pagination.items

    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['BLOG_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False
    
    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author, email=email, site=site, body=body, from_admin=from_admin, post=post, reviewed=reviewed
        )
        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            # send_new_reply_email(replied_comment)
        db.session.add(comment)
        db.session.commit()
        if current_user.is_authenticated:
            flash('Comment published.', 'success')
        else:
            flash('Thanks, your comment will be published after reviewed.', 'info')
            # send_new_comment_email(post)
        return redirect(url_for('.show_post', post_id=post_id))
    return render_template('blog/post.html', post=post, pagination=pagination, form=form, comments=comments)


@blog.route('/about')
def about():
    return render_template('blog/about.html')


@blog.route('/comment/<int:comment_id>/reply')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if not comment.can_comment:
        flash('Comment can not reply', 'waring')
        return redirect(url_for('.show_post', post_id=comment.post_id))
    else:
        return redirect(
            url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form'
        )


@blog.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)


@blog.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BLOG_THEMES'].keys():
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)
    return response
