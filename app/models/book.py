from app.database import db
import datetime


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    cant_pages = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))
    author = db.relationship("Author", backref="books")

    def __init__(self, isbn, name, cant_pages, author_id):
        self.isbn = isbn
        self.name = name
        self.cant_pages = cant_pages
        self.author_id = author_id
