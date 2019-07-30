from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required
from blog.models import Post, Category, Comment, Link, Admin
from blog.extensions import db
from blog.utils import redirect_back
from blog.forms import PostForm, CategoryForm, LinkForm, SettingForm

admin = Blueprint('admin', __name__)


@admin.before_request
@login_required
def login_protect():
    pass


@admin.route('/new_category')
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        return redirect_back()
    return render_template('admin/new_category.html', form=form)


@admin.route('/post/manage')
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_MANAGE_POST_PER_PAGE']
    )
    posts = pagination.items
    return render_template('admin/manage_post.html', pagination=pagination, posts=posts, page=page)


@admin.route('/post/new', methods=['GET', 'POST'])
def new_post():
    form = PostForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        body_html = request.form['fancy-editormd-html-code']
        post = Post(title=title, body=body, category=category, body_html=body_html)
        db.session.add(post)
        db.session.commit()
        flash('Post Created.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@admin.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect_back()


@admin.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)

    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        post.body_html = request.form['fancy-editormd-html-code']
        db.session.commit()
        flash('Post updated.', 'success')

    form.body_html.data = post.body_html
    form.title.data = post.title
    form.category.data = post.category_id
    form.body.data = post.body
    return render_template('admin/edit_post.html', form=form)


@admin.route('/category/manage')
def manage_category():
    categories = Category.query.all()
    return render_template('admin/manage_category.html', categories=categories)


@admin.route('/category/<int:category_id>/edit', methods=['POST'])
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('Can not edit default category', 'waring')
        return redirect(url_for('blog.index'))
    form = CategoryForm()

    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('.manage_category'))
    form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)


@admin.route('/category/<int:category_id>/delete', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('Can not delete default category.', 'waring')
        return redirect(url_for('blog.index'))
    category.delete()
    return redirect(url_for('.manage_category'))


@admin.route('/link/manage')
def manage_link():
    links = Link.query.all()
    return render_template('admin/manage_link.html', links=links)


@admin.route('/link/new', methods=['GET', 'POST'])
def new_link():
    form = LinkForm()

    if form.validate_on_submit():
        name = form.name.data
        url = form.url.data
        link = Link(name=name, url=url)
        db.session.add(link)
        db.session.commit()
        return redirect(url_for('admin.manage_link'))
    return render_template('admin/new_link.html', form=form)


@admin.route('/link/<int:link_id>/edit', methods=['POST'])
def edit_link(link_id):
    link = Link.query.get_or_404(link_id)
    form = LinkForm()

    if form.validate_on_submit():
        link.name = form.name.data
        link.url = form.url.data
        db.session.commit()
        return redirect_back()

    form.name.data = link.name
    form.url.data = link.url
    return render_template('admin/edit_link.html', form=form)


@admin.route('/link/<int:link_id>/delete',  methods=['POST'])
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    return redirect_back()


@admin.route('/comment/manage')
def manage_comment():
    filter_rule = request.args.get('filter', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        filter_comments = Comment.query.filter_by(reviewed=False)
    elif filter_rule == 'admin':
        filter_comments = Comment.query.filter_by(from_admin=True)
    else:
        filter_comments = Comment.query
    pagination = filter_comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', pagination=pagination, comments=comments)


@admin.route('/set-post/<int:post_id>', methods=['GET', 'POST'])
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)

    if post.can_comment:
        post.can_comment = False
        flash('Post comment disabled.', 'success')
    else:
        post.can_comment = True
        flash('Post comment enabled.', 'success')
    db.session.commit()
    return redirect(url_for('blog.show_post', post_id=post_id))


@admin.route('/comment/<int:comment_id>/delete', methods=['POST'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Delete Comment.', 'success')
    return redirect_back()


@admin.route('/comment/<int:comment_id>/approve', methods=['POST'])
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    flash('Comment Approved.', 'success')
    return redirect_back()


@admin.route('/settings', methods=['GET', 'POST'])
def settings():
    admin = Admin.query.first()
    form = SettingForm()
    if form.validate_on_submit():
        admin.blog_title = form.blog_title.data
        admin.blog_sub_title = form.blog_sub_title.data
        admin.about = form.about.data
        admin.name = form.name.data
        db.session.commit()
        return redirect(url_for('blog.index'))

    form.name.data = admin.name
    form.blog_title.data = admin.blog_title
    form.blog_sub_title.data = admin.blog_sub_title
    form.about.data = admin.about

    return render_template('/admin/settings.html', form=form)
