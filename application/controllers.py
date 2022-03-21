import bdb

from flask import Flask, request, render_template, redirect, url_for
from flask import current_app as app
from sqlalchemy import delete

from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt

import numpy as np


from application.models import *



def dateDisplayFormat(date):
    date = datetime.fromisoformat(date)

    # format in required to display in table
    f = "%b %d %I:%M%p"

    return date.strftime(f)

def dateSqlFormat(date):
    # converting string to datetime object
    date = datetime.fromisoformat(date)

    # format in required to store in SQL table
    f = "%Y-%m-%d %H:%M:%S"

    return date.strftime(f)

def dateHtmlFormate(date):
    date = date[:10] + "T" + date[11:-3]
    return date



#----------------------------Login------------------------------------
@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    else:
        username = request.form['username']
        password = request.form['password']

        if len(username) ==0 or len(password) == 0:
            return render_template('mandatory_login.html')

        member = User.query.filter(User.username == username).first()

        if member == None:
            return render_template("no_such_user.html")

        if member.username == username:
            if member.password != password:
                return render_template("wrong_password.html")

        user_id = member.user_id
        return redirect(url_for('home_page', user_id=user_id))


@app.route("/<int:user_id>/homepage", methods=["GET"])
def home_page(user_id):
    member = User.query.filter(User.user_id == user_id).first()

    moods = MoodTracker.query.filter(MoodTracker.user_id == user_id).order_by(MoodTracker.date.desc()).first()
    runs = RunTracker.query.filter(RunTracker.user_id == user_id).order_by(RunTracker.date.desc()).first()
    temps = TempTracker.query.filter(TempTracker.user_id == user_id).order_by(TempTracker.date.desc()).first()

    mood_date=None
    run_date=None
    temp_date=None

    if(moods):
        mood_date = dateDisplayFormat(moods.date)

    if(runs):
        run_date = dateDisplayFormat(runs.date)

    if(temps):
        temp_date = dateDisplayFormat(temps.date)

    return render_template("view_user.html", member=member, moods=moods, runs=runs, temps=temps,
                           mood_date=mood_date, run_date=run_date, temp_date=temp_date)


# ---------------------Registration------------------------------------
@app.route("/new_registration", methods=["GET", "POST"])
def new_register():
    if request.method == 'GET':
        return render_template('new_register.html')

    else:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if len(username) == 0 or len(email) == 0 or len(password) == 0:
            return render_template('mandatory_details.html')

        if User.query.filter(User.username == username).first():
            return render_template('username_already_exists.html')

        if User.query.filter(User.email == email).first():
            return render_template('email_already_exists.html')

        s = User(username=username, email=email, password=password)

        db.session.add(s)
        db.session.commit()

        return redirect(url_for('login'))

#---------------------Running Tracker -------------------------------

@app.route("/RunningTracker/<int:user_id>", methods=["GET"])
def run_tracker_view(user_id):
    member = User.query.filter(User.user_id == user_id).first()
    runs = RunTracker.query.filter(RunTracker.user_id == user_id).order_by(RunTracker.date.desc()).all()

    dates = []
    for i in runs:
        dates.append(dateDisplayFormat(i.date))

    values = []
    for i in runs:
        values.append(i.value)

    dates.reverse()
    values.reverse()

    x = np.array(list(range(len(dates))))
    y = np.array(values)

    plt.figure(figsize=(12,6))
    plt.xlabel('Events')
    plt.ylabel("Distance in Km")
    plt.ylim(0, 15)
    plt.plot(x, y, color='g', marker='o', linestyle='--')

    plt.savefig('static/run_graph.png')

    dates.reverse()

    return render_template('run_tracker_view.html', member=member, dates=dates, runs=runs)

@app.route("/RunningTracker/<user_id>/Delete", methods=["GET"])
def run_tracker_delete(user_id):
    stmt = delete(RunTracker).where(RunTracker.user_id == user_id)

    db.session.execute(stmt)
    db.session.commit()

    return redirect(url_for('home_page', user_id=user_id))



@app.route("/RunningTracker/<int:user_id>/AddEntry", methods=["GET", "POST"])
def run_tracker_add(user_id):
    member = User.query.filter(User.user_id == user_id).first()

    if request.method == "GET":
        return render_template("run_tracker_add.html", member=member)

    else:
        when = request.form["when"]
        value = request.form['value']
        notes = request.form['notes']

        # converting when to format accepted to SQL Format
        when = dateSqlFormat(when)

        run = RunTracker(value=value, desc=notes, date=when, user_id=user_id)

        db.session.add(run)
        db.session.commit()

        return redirect(url_for('run_tracker_view',user_id=user_id))

@app.route('/RunningTracker/<int:user_id>/DeleteEntry/<int:run_id>')
def run_delete_entry(run_id, user_id):
    run = RunTracker.query.filter(RunTracker.track_id == run_id).first()

    db.session.delete(run)
    db.session.commit()
    return redirect(url_for('run_tracker_view', user_id=user_id))

@app.route('/RunningTracker/<int:user_id>/EditEntry/<int:run_id>',methods=["GET", "POST"])
def run_edit_entry(run_id, user_id):
    member = User.query.filter(User.user_id == user_id).first()

    run = RunTracker.query.filter(RunTracker.track_id == run_id).first()

    if request.method == "GET":
        date = dateHtmlFormate(run.date)
        notes = run.desc[:]
        # return date
        return render_template('run_tracker_edit.html', member=member, run=run, date=date, notes=notes)

    else:
        when = request.form["when"]
        value = request.form['value']
        notes = request.form['notes']

        # converting when to format accepted to SQL Format
        when = dateSqlFormat(when)

        run_up = RunTracker.query.filter(RunTracker.track_id == run_id).first()
        run_up.date = when
        run_up.value = value
        run_up.desc = notes

        db.session.commit()
        return redirect(url_for('run_tracker_view', user_id=user_id))



#---------------------Temperature Tracker-------------------------------

@app.route("/TemperatureTracker/<int:user_id>", methods=["GET"])
def temp_tracker_view(user_id):
    if request.method == 'GET':
        member = User.query.filter(User.user_id == user_id).first()
        temps = TempTracker.query.filter(TempTracker.user_id == user_id).order_by(TempTracker.date.desc()).all()

        dates = []
        for i in temps:
            dates.append(dateDisplayFormat(i.date))

        values = []
        for i in temps:
            values.append(i.value)

        dates.reverse()
        values.reverse()

        x = np.array(list(range(len(dates))))
        y = np.array(values)

        plt.figure(figsize=(12, 6))
        plt.xlabel('Events')
        plt.ylabel("Body Temperature in Fahrenheit!")
        plt.ylim(95, 110)
        plt.plot(x, y, color='r', marker='o', linestyle='--')

        plt.savefig('static/temp_graph.png')

        dates.reverse()

        return render_template('temp_tracker_view.html', member=member, dates=dates, temps=temps)

@app.route("/TemperatureTracker/<user_id>/Delete", methods=["GET"])
def temp_tracker_delete(user_id):
    stmt = delete(TempTracker).where(TempTracker.user_id == user_id)

    db.session.execute(stmt)
    db.session.commit()

    return redirect(url_for('home_page', user_id=user_id))


@app.route("/TemperatureTracker/<int:user_id>/AddEntry", methods=["GET", "POST"])
def temp_tracker_add(user_id):
    member = User.query.filter(User.user_id == user_id).first()

    if request.method == "GET":
        return render_template("temp_tracker_add.html", member=member)

    else:
        when = request.form["when"]
        value = request.form['value']
        notes = request.form['notes']

        # converting when to format accepted to SQL Format
        when = dateSqlFormat(when)

        temp = TempTracker(value=value, desc=notes, date=when, user_id=user_id)

        db.session.add(temp)
        db.session.commit()

        return redirect(url_for('temp_tracker_view',user_id=user_id))

@app.route('/TemperatureTracker/<int:user_id>/DeleteEntry/<int:temp_id>')
def temp_delete_entry(temp_id, user_id):
    temp = TempTracker.query.filter(TempTracker.track_id == temp_id).first()

    db.session.delete(temp)
    db.session.commit()
    return redirect(url_for('temp_tracker_view', user_id=user_id))

@app.route('/TemperatureTracker/<int:user_id>/EditEntry/<int:temp_id>',methods=["GET", "POST"])
def temp_edit_entry(temp_id, user_id):
    member = User.query.filter(User.user_id == user_id).first()

    temp = TempTracker.query.filter(TempTracker.track_id == temp_id).first()

    if request.method == "GET":
        date = dateHtmlFormate(temp.date)
        notes = temp.desc[:]
        # return date
        return render_template('temp_tracker_edit.html', member=member, temp=temp, date=date, notes=notes)

    else:
        when = request.form["when"]
        value = request.form['value']
        notes = request.form['notes']

        # converting when to format accepted to SQL Format
        when = dateSqlFormat(when)

        temp_up = TempTracker.query.filter(TempTracker.track_id == temp_id).first()
        temp_up.date = when
        temp_up.value = value
        temp_up.desc = notes

        db.session.commit()
        return redirect(url_for('temp_tracker_view', user_id=user_id))



#---------------------Mood Tracker View-------------------------------
@app.route("/MoodTracker/<int:user_id>", methods=["GET",])
def mood_tracker_view(user_id):
    if request.method == 'GET':
        member = User.query.filter(User.user_id == user_id).first()
        moods = MoodTracker.query.filter(MoodTracker.user_id == user_id).order_by(MoodTracker.date.desc()).all()

        dates = []
        for i in moods:
            dates.append(dateDisplayFormat(i.date))

        values = []
        for i in moods:
            values.append(i.value)

        mood_count = {}
        for i in values:
            mood_count[i] = values.count(i)

        x = np.array(list(mood_count.keys()))
        y = np.array(list(mood_count.values()))

        plt.figure(figsize=(12, 6))
        plt.xlabel('Moods')
        plt.ylabel("Frequency of Mood ")
        plt.ylim(0,10)
        plt.bar(x, y, color='b')

        plt.savefig('static/mood_graph.png')


        return render_template('mood_tracker_view.html', member=member, dates=dates, moods=moods)


@app.route("/MoodTracker/<user_id>/Delete", methods=["GET"])
def mood_tracker_delete(user_id):
    stmt = delete(MoodTracker).where(MoodTracker.user_id == user_id)

    db.session.execute(stmt)
    db.session.commit()

    return redirect(url_for('home_page', user_id=user_id))



@app.route("/MoodTracker/<int:user_id>/AddEntry", methods=["GET", "POST"])
def mood_tracker_add(user_id):
    member = User.query.filter(User.user_id == user_id).first()
    mood_values = ['Angry', 'Sad', 'Happy', 'Calm', 'Okay', 'Meh']

    if request.method == "GET":
        return render_template("mood_tracker_add.html", member=member, mood_values=mood_values)

    else:
        when = request.form["when"]
        value = request.form['value']
        notes = request.form['notes']

        # converting when to format accepted to SQL Format
        when = dateSqlFormat(when)

        mood = MoodTracker(value=value, desc=notes, date=when, user_id=user_id)

        db.session.add(mood)
        db.session.commit()

        return redirect(url_for('mood_tracker_view',user_id=user_id))

@app.route('/MoodTracker/<int:user_id>/DeleteEntry/<int:mood_id>')
def mood_delete_entry(mood_id, user_id):
    mood = MoodTracker.query.filter(MoodTracker.track_id == mood_id).first()

    db.session.delete(mood)
    db.session.commit()
    return redirect(url_for('mood_tracker_view', user_id=user_id))

@app.route('/MoodTracker/<int:user_id>/EditEntry/<int:mood_id>',methods=["GET", "POST"])
def mood_edit_entry(mood_id, user_id):
    member = User.query.filter(User.user_id == user_id).first()
    mood_values = ['Angry', 'Sad', 'Happy', 'Calm', 'Okay', 'Meh']

    mood = MoodTracker.query.filter(MoodTracker.track_id == mood_id).first()

    if request.method == "GET":
        date = dateHtmlFormate(mood.date)
        notes = mood.desc[:]
        # return date
        return render_template('mood_tracker_edit.html', member=member, mood=mood, date=date, mood_values=mood_values)

    else:
        when = request.form["when"]
        value = request.form['value']
        notes = request.form['notes']

        # converting when to format accepted to SQL Format
        when = dateSqlFormat(when)

        mood_up = MoodTracker.query.filter(MoodTracker.track_id == mood_id).first()
        mood_up.date = when
        mood_up.value = value
        mood_up.desc = notes

        db.session.commit()
        return redirect(url_for('mood_tracker_view', user_id=user_id))