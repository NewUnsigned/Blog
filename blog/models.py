from blog.extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# 管理员
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    blog_title = db.Column(db.String(60))
    blog_sub_title = db.Column(db.String(100))
    name = db.Column(db.String(30))
    about = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    # 分类有多个文章
    # posts对应了Post的category属性
    posts = db.relationship('Post', back_populates='category')

    def delete(self):
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # 文章只有一个分类
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    # 文章和文类一对多的关系category对应了Post的posts
    category = db.relationship('Category', back_populates='posts')
    # 设置级联关系，当文章删除后，该文章的评论也一并删除
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')

    can_comment = db.Column(db.Boolean, default=True)


# 评论
# 每篇文章都可以包含多个评论，文章和评论之间是一对多的双向关系
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    email = db.Column(db.String(254))
    site = db.Column(db.String(255))
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False)
    # 是否通过审核
    reviewed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', back_populates='comments')

    # 同一个模型内的一对多关系，在SQLAlchemy中被称为邻接列表关系
    # Comment中添加一个外键指向它自身，这样每个评论对象都可以包含多个子回复评论
    # replies评论对应的多个回复评论
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
    # 回复评论的id，其实就是评论的id，一对多中多的外键
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    # 回复的评论
    # remote_side为id：把id字段定义为关系的远程侧，而replied_id就相应的变为本地侧
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])


class Link(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(20))
    url = db.Column(db.String(255))
