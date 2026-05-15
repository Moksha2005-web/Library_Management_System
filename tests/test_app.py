import pytest
from app import create_app, db
from app.models import Book, Member, Issue
from datetime import datetime, timedelta


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret'
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_book(app):
    with app.app_context():
        book = Book(title='Test Book', author='Test Author',
                    isbn='123-456', genre='Fiction', quantity=3, available=3)
        db.session.add(book)
        db.session.commit()
        return book.id


@pytest.fixture
def sample_member(app):
    with app.app_context():
        member = Member(name='Test User', email='test@example.com',
                        phone='9999999999', member_id='MEM99999')
        db.session.add(member)
        db.session.commit()
        return member.id


# ─── Health & Dashboard ───────────────────────────────────────────────────────

def test_health_endpoint(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'healthy'


def test_dashboard_loads(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Dashboard' in resp.data


# ─── Books ────────────────────────────────────────────────────────────────────

def test_books_page(client):
    resp = client.get('/books')
    assert resp.status_code == 200


def test_add_book(client):
    resp = client.post('/books/add', data={
        'title': 'Clean Code',
        'author': 'Robert Martin',
        'isbn': '978-0132350884',
        'genre': 'Technology',
        'quantity': '2'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Clean Code' in resp.data


def test_add_book_duplicate_isbn(client, app):
    """Duplicate ISBN should not create a second book (DB enforces uniqueness)."""
    data = dict(title='Book A', author='Author', isbn='DUP-001', genre='', quantity='1')
    client.post('/books/add', data=data, follow_redirects=True)
    try:
        client.post('/books/add', data=data, follow_redirects=True)
    except Exception:
        pass  # IntegrityError is the expected behaviour
    with app.app_context():
        count = Book.query.filter_by(isbn='DUP-001').count()
        assert count == 1  # only one book should exist


def test_api_books(client, sample_book):
    resp = client.get('/api/books')
    assert resp.status_code == 200
    books = resp.get_json()
    assert len(books) >= 1
    assert books[0]['title'] == 'Test Book'


def test_delete_book(client, app, sample_book):
    resp = client.post(f'/books/delete/{sample_book}', follow_redirects=True)
    assert resp.status_code == 200
    with app.app_context():
        assert Book.query.get(sample_book) is None


# ─── Members ─────────────────────────────────────────────────────────────────

def test_members_page(client):
    resp = client.get('/members')
    assert resp.status_code == 200


def test_add_member(client):
    resp = client.post('/members/add', data={
        'name': 'Priya Sharma',
        'email': 'priya@example.com',
        'phone': '9876543210'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Priya Sharma' in resp.data


def test_api_members(client, sample_member):
    resp = client.get('/api/members')
    assert resp.status_code == 200
    members = resp.get_json()
    assert any(m['name'] == 'Test User' for m in members)


# ─── Issues ──────────────────────────────────────────────────────────────────

def test_issues_page(client):
    resp = client.get('/issues')
    assert resp.status_code == 200


def test_issue_book(client, app, sample_book, sample_member):
    resp = client.post('/issues/add', data={
        'book_id': str(sample_book),
        'member_id': str(sample_member)
    }, follow_redirects=True)
    assert resp.status_code == 200
    with app.app_context():
        issue = Issue.query.first()
        assert issue is not None
        assert issue.status == 'issued'
        book = Book.query.get(sample_book)
        assert book.available == 2   # was 3, now 2


def test_return_book(client, app, sample_book, sample_member):
    client.post('/issues/add', data={
        'book_id': str(sample_book),
        'member_id': str(sample_member)
    })
    with app.app_context():
        issue = Issue.query.first()
        issue_id = issue.id

    resp = client.post(f'/issues/return/{issue_id}', follow_redirects=True)
    assert resp.status_code == 200
    with app.app_context():
        issue = Issue.query.get(issue_id)
        assert issue.status == 'returned'
        assert issue.return_date is not None
        book = Book.query.get(sample_book)
        assert book.available == 3   # restored


def test_api_issues(client, app, sample_book, sample_member):
    client.post('/issues/add', data={
        'book_id': str(sample_book),
        'member_id': str(sample_member)
    })
    resp = client.get('/api/issues')
    assert resp.status_code == 200
    issues = resp.get_json()
    assert len(issues) == 1
