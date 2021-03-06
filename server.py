import os
from flask import Flask, render_template, request, flash, redirect, session, abort
from flask_debugtoolbar import DebugToolbarExtension
import requests
from datetime import datetime
from model import connect_to_db, db, User, Entry, Tag, EntryTag
import json
import pdb
from flask_login import login_required, current_user
from flask_bcrypt import Bcrypt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from flask.ext.login import current_user,current_app
from sqlalchemy import func


app = Flask(__name__)

app.secret_key = "Shhhhh"

bcrypt = Bcrypt(app)


@app.route('/')
def homepage():
    """Display the homepage to the user"""

    quote, quote_author = get_quotes_for_footer()

    if not session.get('logged_in'):
        return render_template("homepage.html",
                               quote=quote,
                               quote_author=quote_author)
    else:
        return render_template("entry.html",
                               quote=quote,
                               quote_author=quote_author)


@app.route('/login', methods=['POST'])
def handle_login():
    """Process login and store user in session."""

    # this function handles the form info from the homepage modal window
    username = request.form["username"]
    password = bcrypt.generate_password_hash(request.form.get("password"))

    # Check that the user exists.
    uq = User.query
    user_object = uq.filter_by(username=username).first()

    if user_object and bcrypt.check_password_hash(password, user_object.password):

        session["user_id"] = user_object.user_id
        session["logged_in"] = True

        flash("Hello again - You are logged in!")
        quote, quote_author = get_quotes_for_footer()

        return render_template("entry.html",
                                quote=quote,
                                quote_author=quote_author)

    else:
        flash("Incorrect login")
        return redirect("/")

# https://www.reddit.com/r/flask/comments/1vziqt/flaskwtf_multiple_forms_on_page_headache/


@app.route('/register', methods=['POST'])
def register():

    username = request.form["username"]
    email = request.form["email"]
    password = bcrypt.generate_password_hash(request.form.get("password"))

    # Autoincrements user_id
    user_id = db.session.query(func.max(User.user_id + 1))
    
    # Add the new user to the model
    new_user = User(user_id=user_id, username=username, password=password, email=email)


    db.session.add(new_user)
    db.session.commit()

    # Add the user to the session
    session["logged_in"] = True

    flash("""You have just registered! Login to start writing entries. 
          Thank you!""")

    quote, quote_author = get_quotes_for_footer()

    return render_template("entry.html",
                           quote=quote,
                           quote_author=quote_author)


@app.route('/new_entry')
def new_entry():
    """Displays new journal entry form."""

    quote, quote_author = get_quotes_for_footer()

    return render_template("entry.html",
                           quote=quote,
                           quote_author=quote_author)


@app.route('/view_entries', methods=['GET', 'POST'])
def add_entry_to_db():
    """Save and redirect journal entries."""

    try:
        title = request.form["title"]
        print "\n\n\n\n title", title
        body = request.form["journalBody"]
        print "\n\n\n\n\n journal body", body
        tags = request.form.getlist('prof1')
        print "\n\n\n\n tags", tags

        user_id = session['user_id']
        print "\n\n\n\n user_id", user_id

        entry = Entry(entry_body=body, entry_title=title, user_id=user_id)

        # Need to consider entry_date
        # entry_id = Entry(body=entry_body, entry_date=entry_date, username=username, tag=tag)

        db.session.add(entry)
        db.session.commit()

        user_entries = Entry.query.filter(Entry.user_id == user_id).all()

        quote, quote_author = get_quotes_for_footer()

        return render_template("view_entries.html",
                               user_entries=user_entries,
                               title=title,
                               body=body,
                               quote=quote,
                               quote_author=quote_author)
    except:

        quote, quote_author = get_quotes_for_footer()

        return render_template("error.html",
                               quote=quote,
                               quote_author=quote_author)


# This works if the user has entries
@app.route('/view_entries_submitted', methods=['GET', 'POST'])
def view_entries():
    """User views their entries from the navbar link"""

    # Get the user from the session
    if "user_id" in session:
        user_id = session["user_id"] 

        # Query the DB to get all entries
        
        user_entries = Entry.query.filter(Entry.user_id == user_id).all()
        
        # Include the navbar bottom for quotes
        quote, quote_author = get_quotes_for_footer()

        try:
            return render_template("view_entries.html", 
                            user_entries=user_entries,
                            quote=quote,
                            quote_author=quote_author)
        except:
            return render_template("error.html",
                                    quote=quote,
                                    quote_author=quote_author)


@app.route('/logout')
def logout_form():
    """Process logout form"""

    #Remove user from session
    session.clear()

    return redirect("/")


@app.route('/recover', methods=('GET', 'POST', ))
def recover_login_info():
    """When the user hits forgot password in the login modal, send them an email with their username or password"""
    token = request.args.get('token', None)
    form = ResetPassword(request.form)
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.get_token()
            print token
    return redirect("/")

########################### Helper Functions ###################################

def get_quotes_for_footer():
    """Call this function in other routes to display fancy quote footer"""
    try:
        r = requests.get("http://api.forismatic.com/api/1.0/?method=getQuote&format=json&lang=en")
        quote = r.json()["quoteText"]

        quote_author = r.json()["quoteAuthor"]

    except:
        quote = unicode("Through perseverance many people win success out of what seemed destined to be certain failure.", "utf-8")
        quote_author = unicode("Benjamin Disraeli", "utf-8")

    return quote, quote_author


if __name__ == "__main__":
    DebugToolbarExtension(app)

    connect_to_db(app)

    app.run(debug=True, host='0.0.0.0', port=5000) #vagrant requires port to be 5000
