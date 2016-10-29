import os 
from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
import requests
from datetime import datetime
from model import User, Entry, Tag, EntryTag
import json
import pdb

app = Flask(__name__)

app.secret_key = "Shhhhh"

@app.route('/')
def homepage():
    """Display the homepage to the user"""

    return render_template("homepage.html")

@app.route('/register', methods=['POST'])
def register():
    """Register the user"""
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    #add the new user to the model
    new_user = User(username=username, password=password, email=email)

    db.session.add(new_user)
    db.session.commit()

    flash("You have just registered! Thank you!")
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    """Login the user"""
    #this function handles the form info from the homepage modal window 
    email = request.form("email")
    password = request.form["password"]

def view_entries_by_tag():
    """Create a function that sorts the entries by user's input tag"""

@app.route('/new_entry')
def add_entry_to_db():
    entry_body = request.form["entry"]
    # add the entry to the model
    entry_id = Entry(entry_body=entry_body, entry_date=entry_date, username=username, tag=tag)

    db.session.add(entry_id)
    db.session.commit()

if __name__ == "__main__":
    DebugToolbarExtension(app)

    app.run(debug=True, host='0.0.0.0', port=5000) #vagrant requires port to be 5000