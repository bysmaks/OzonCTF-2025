import databases
import ormar
import sqlalchemy
from config import settings

database = databases.Database(settings.db_url)
metadata = sqlalchemy.MetaData()


class User(ormar.Model):
    ormar_config = ormar.OrmarConfig(
        database=database,
        metadata=metadata,
        tablename='users'
    )

    id: int = ormar.Integer(primary_key=True)
    username: str = ormar.String(max_length=128, unique=True, nullable=False)
    password: str = ormar.String(max_length=128, nullable=False)


class TextEntry(ormar.Model):
    ormar_config = ormar.OrmarConfig(
        database=database,
        metadata=metadata,
        tablename='text_entries'
    )

    id: int = ormar.Integer(primary_key=True)
    content: str = ormar.Text()
    user: User = ormar.ForeignKey(User)



engine = sqlalchemy.create_engine(settings.db_url)
metadata.create_all(engine)
