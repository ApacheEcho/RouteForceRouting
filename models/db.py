import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base

db = SQLAlchemy()
Base = declarative_base()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()