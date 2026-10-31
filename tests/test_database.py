import pytest

from src.ext.database import db, add_all


class Item(db.Model):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


@pytest.fixture
def app():
    app = __import__("flask").Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
    yield app


def test_add_all_commits_all_rows(app):
    with app.app_context():
        add_all([Item(name="a"), Item(name="b")])
        assert db.session.query(Item).count() == 2