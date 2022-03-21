from .database import db

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    run_tracks = db.relationship('RunTracker', backref='user', lazy=True)

    temp_tracks = db.relationship('TempTracker', backref='user', lazy=True)

    mood_tracks = db.relationship('MoodTracker', backref='user', lazy=True)




class RunTracker(db.Model):
    __tablename__= 'run_tracker'
    __table_args__ = (
        db.CheckConstraint("value > 0 AND value < 22.1"),
    )
    track_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.Float, nullable=False,)
    desc = db.Column(db.String,)
    date = db.Column(db.String, nullable=False,)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

class TempTracker(db.Model):
    __tablename__= 'temp_tracker'
    __table_args__ = (
        db.CheckConstraint("value > 97 AND value < 112"),
    )

    track_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.Float, nullable=False)
    desc = db.Column(db.String)
    date = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)


class MoodTracker(db.Model):
    __tablename__ = 'mood_tracker'
    __table_args__ = (
        db.CheckConstraint("value IN ('Angry', 'Sad', 'Happy', 'Calm', 'Okay', 'Meh')"),)

    track_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    value = db.Column(db.String,nullable=False,)
    desc = db.Column(db.String)
    date = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)