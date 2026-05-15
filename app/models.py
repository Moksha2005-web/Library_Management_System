from app import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    genre = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=1)
    available = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    issues = db.relationship('Issue', backref='book', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'genre': self.genre,
            'quantity': self.quantity,
            'available': self.available
        }


class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    member_id = db.Column(db.String(20), unique=True, nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    issues = db.relationship('Issue', backref='member', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'member_id': self.member_id
        }


class Issue(db.Model):
    __tablename__ = 'issues'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='issued')  # issued / returned

    def to_dict(self):
        return {
            'id': self.id,
            'book': self.book.title if self.book else None,
            'member': self.member.name if self.member else None,
            'issue_date': self.issue_date.strftime('%Y-%m-%d'),
            'due_date': self.due_date.strftime('%Y-%m-%d'),
            'return_date': self.return_date.strftime('%Y-%m-%d') if self.return_date else None,
            'status': self.status
        }
