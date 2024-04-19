import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Answers(SqlAlchemyBase):
    __tablename__ = 'answer'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    answer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    question_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("quest.id"))
    question = sqlalchemy.orm.relationship('Questions')

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = sqlalchemy.orm.relationship('User')

