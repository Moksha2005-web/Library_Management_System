from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from app.models import Book, Member, Issue
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

# ─── Dashboard ───────────────────────────────────────────────────────────────

@main.route('/')
def index():
    total_books   = Book.query.count()
    total_members = Member.query.count()
    active_issues = Issue.query.filter_by(status='issued').count()
    overdue = Issue.query.filter(
        Issue.status == 'issued',
        Issue.due_date < datetime.utcnow()
    ).count()
    recent_issues = Issue.query.order_by(Issue.issue_date.desc()).limit(5).all()
    return render_template('index.html',
                           total_books=total_books,
                           total_members=total_members,
                           active_issues=active_issues,
                           overdue=overdue,
                           recent_issues=recent_issues)

# ─── Books ────────────────────────────────────────────────────────────────────

@main.route('/books')
def books():
    all_books = Book.query.all()
    return render_template('books.html', books=all_books)

@main.route('/books/add', methods=['POST'])
def add_book():
    data = request.form
    book = Book(
        title    = data['title'],
        author   = data['author'],
        isbn     = data['isbn'],
        genre    = data.get('genre', ''),
        quantity = int(data.get('quantity', 1)),
        available= int(data.get('quantity', 1))
    )
    db.session.add(book)
    db.session.commit()
    flash('Book added successfully!', 'success')
    return redirect(url_for('main.books'))

@main.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted.', 'info')
    return redirect(url_for('main.books'))

# ─── Members ─────────────────────────────────────────────────────────────────

@main.route('/members')
def members():
    all_members = Member.query.all()
    return render_template('members.html', members=all_members)

@main.route('/members/add', methods=['POST'])
def add_member():
    data = request.form
    import random, string
    mid = 'MEM' + ''.join(random.choices(string.digits, k=5))
    member = Member(
        name      = data['name'],
        email     = data['email'],
        phone     = data.get('phone', ''),
        member_id = mid
    )
    db.session.add(member)
    db.session.commit()
    flash(f'Member added! ID: {mid}', 'success')
    return redirect(url_for('main.members'))

@main.route('/members/delete/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash('Member removed.', 'info')
    return redirect(url_for('main.members'))

# ─── Issues ──────────────────────────────────────────────────────────────────

@main.route('/issues')
def issues():
    all_issues = Issue.query.order_by(Issue.issue_date.desc()).all()
    books   = Book.query.filter(Book.available > 0).all()
    members = Member.query.all()
    return render_template('issues.html', issues=all_issues, books=books, members=members)

@main.route('/issues/add', methods=['POST'])
def add_issue():
    data    = request.form
    book    = Book.query.get_or_404(int(data['book_id']))
    if book.available < 1:
        flash('No copies available!', 'danger')
        return redirect(url_for('main.issues'))
    due = datetime.utcnow() + timedelta(days=14)
    issue = Issue(
        book_id   = book.id,
        member_id = int(data['member_id']),
        due_date  = due
    )
    book.available -= 1
    db.session.add(issue)
    db.session.commit()
    flash('Book issued successfully!', 'success')
    return redirect(url_for('main.issues'))

@main.route('/issues/return/<int:issue_id>', methods=['POST'])
def return_book(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    issue.status      = 'returned'
    issue.return_date = datetime.utcnow()
    issue.book.available += 1
    db.session.commit()
    flash('Book returned successfully!', 'success')
    return redirect(url_for('main.issues'))

# ─── Health check (for Docker/Jenkins) ───────────────────────────────────────

@main.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Library Management System'}), 200

# ─── API endpoints ────────────────────────────────────────────────────────────

@main.route('/api/books')
def api_books():
    return jsonify([b.to_dict() for b in Book.query.all()])

@main.route('/api/members')
def api_members():
    return jsonify([m.to_dict() for m in Member.query.all()])

@main.route('/api/issues')
def api_issues():
    return jsonify([i.to_dict() for i in Issue.query.all()])
