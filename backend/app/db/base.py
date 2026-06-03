from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def create_db_and_tables() -> None:
    from app.models.entities import import_models

    import_models()
    from app.db.session import engine

    Base.metadata.create_all(bind=engine)
