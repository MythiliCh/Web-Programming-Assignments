from flask import Flask, render_template, request, make_response, redirect
from session_db import create_session, delete_session, get_session
from mongita import MongitaClientDisk
from bson import ObjectId

app = Flask(__name__)
client = MongitaClientDisk()

# open the quotes database
quotes_db = client.quotes_db
session_db = client.session_db

import uuid

# Function to retrieve quotes for a user

@app.route("/register", methods=["GET"])
def get_register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def post_register():
    # Handle registration form submission here
    return redirect("/login")

def get_quotes_for_user(user):
    quotes_collection = client.quotes_db.quotes_collection
    data = list(quotes_collection.find({"owner": user}))
    for item in data:
        item["_id"] = str(item["_id"])
    return data

@app.route("/", methods=["GET"])
@app.route("/quotes", methods=["GET"])
def get_quotes():
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        return redirect("/login")
    session_data = get_session(session_id)
    if not session_data:
        return redirect("/logout")
    user = session_data.get("user", "unknown user")
    data = get_quotes_for_user(user)
    return render_template("quotes.html", data=data, user=user)

@app.route("/login", methods=["GET"])
def get_login():
    session_id = request.cookies.get("session_id", None)
    if session_id:
        return redirect("/quotes")
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def post_login():
    user = request.form.get("user", "")
    session_id = create_session(user)
    response = redirect("/quotes")
    response.set_cookie("session_id", session_id)
    return response

@app.route("/logout", methods=["GET"])
def get_logout():
    session_id = request.cookies.get("session_id", None)
    if session_id:
        delete_session(session_id)
    response = redirect("/login")
    response.delete_cookie("session_id")
    return response

@app.route("/add", methods=["GET"])
def get_add():
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        return redirect("/login")
    return render_template("add_quote.html")

@app.route("/add", methods=["POST"])
def post_add():
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        return redirect("/login")
    session_data = get_session(session_id)
    if not session_data:
        return redirect("/logout")
    user = session_data.get("user", "unknown user")
    text = request.form.get("text", "")
    author = request.form.get("author", "")
    if text and author:
        quotes_collection = client.quotes_db.quotes_collection
        quote_data = {"owner": user, "text": text, "author": author}
        quotes_collection.insert_one(quote_data)
    return redirect("/quotes")

@app.route("/edit/<id>", methods=["GET"])
def get_edit(id=None):
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        return redirect("/login")
    session_data = get_session(session_id)
    if not session_data:
        return redirect("/logout")
    if id:
        quotes_collection = client.quotes_db.quotes_collection
        data = quotes_collection.find_one({"_id": ObjectId(id)})
        data["id"] = str(data["_id"])
        return render_template("edit_quote.html", data=data)
    return redirect("/quotes")

@app.route("/edit", methods=["POST"])
def post_edit():
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        return redirect("/login")
    _id = request.form.get("_id", None)
    text = request.form.get("text", "")
    author = request.form.get("author", "")
    if _id:
        session_data = get_session(session_id)
        if not session_data:
            return redirect("/logout")
        user = session_data.get("user", "unknown user")
        quotes_collection = client.quotes_db.quotes_collection
        values = {"$set": {"text": text, "author": author}}
        data = quotes_collection.update_one({"_id": ObjectId(_id), "owner": user}, values)
    return redirect("/quotes")

@app.route("/delete", methods=["GET"])
@app.route("/delete/<id>", methods=["GET"])
def get_delete(id=None):
    session_id = request.cookies.get("session_id", None)
    if not session_id:
        return redirect("/login")
    session_data = get_session(session_id)
    if not session_data:
        return redirect("/logout")
    if id:
        quotes_collection = client.quotes_db.quotes_collection
        quotes_collection.delete_one({"_id": ObjectId(id)})
    return redirect("/quotes")

# from flask import Flask, render_template, request, make_response, redirect
# from mongita import MongitaClientDisk
# from bson import ObjectId

# app = Flask(__name__)

# # create a mongita client connection
# client = MongitaClientDisk()

# # open the quotes database
# quotes_db = client.quotes_db
# session_db = client.session_db

# import uuid

# @app.route("/", methods=["GET"])
# @app.route("/quotes", methods=["GET"])
# def get_quotes():
#     session_id = request.cookies.get("session_id", None)
#     if not session_id:
#         response = redirect("/login")
#         return response
#     # open the session collection
#     session_collection = session_db.session_collection
#     # get the data for this session
#     session_data = list(session_collection.find({"session_id": session_id}))
#     if len(session_data) == 0:
#         response = redirect("/logout")
#         return response
#     assert len(session_data) == 1
#     session_data = session_data[0]
#     # get some information from the session
#     user = session_data.get("user", "unknown user")
#     # open the quotes collection
#     quotes_collection = quotes_db.quotes_collection
#     # load the data
#     data = list(quotes_collection.find({"owner":user}))
#     for item in data:
#         item["_id"] = str(item["_id"])
#         item["object"] = ObjectId(item["_id"])
#     # display the data
#     html = render_template(
#         "quotes.html",
#         data=data,
#         user=user,
#     )
#     response = make_response(html)
#     response.set_cookie("session_id", session_id)
#     return response


# @app.route("/login", methods=["GET"])
# def get_login():
#     session_id = request.cookies.get("session_id", None)
#     print("Pre-login session id = ", session_id)
#     if session_id:
#         return redirect("/quotes")
#     return render_template("login.html")


# @app.route("/login", methods=["POST"])
# def post_login():
#     user = request.form.get("user", "")
#     session_id = str(uuid.uuid4())
#     # open the session collection
#     session_collection = session_db.session_collection
#     # insert the user
#     session_collection.delete_one({"session_id": session_id})
#     session_data = {"session_id": session_id, "user": user}
#     session_collection.insert_one(session_data)
#     response = redirect("/quotes")
#     response.set_cookie("session_id", session_id)
#     return response


# @app.route("/logout", methods=["GET"])
# def get_logout():
#     # get the session id
#     session_id = request.cookies.get("session_id", None)
#     if session_id:
#         # open the session collection
#         session_collection = session_db.session_collection
#         # delete the session
#         session_collection.delete_one({"session_id": session_id})
#     response = redirect("/login")
#     response.delete_cookie("session_id")
#     return response


# @app.route("/add", methods=["GET"])
# def get_add():
#     session_id = request.cookies.get("session_id", None)
#     if not session_id:
#         response = redirect("/login")
#         return response
#     return render_template("add_quote.html")


# @app.route("/add", methods=["POST"])
# def post_add():
#     session_id = request.cookies.get("session_id", None)
#     if not session_id:
#         response = redirect("/login")
#         return response
#     # open the session collection
#     session_collection = session_db.session_collection
#     # get the data for this session
#     session_data = list(session_collection.find({"session_id": session_id}))
#     if len(session_data) == 0:
#         response = redirect("/logout")
#         return response
#     assert len(session_data) == 1
#     session_data = session_data[0]
#     # get some information from the session
#     user = session_data.get("user", "unknown user")
#     text = request.form.get("text", "")
#     author = request.form.get("author", "")
#     if text != "" and author != "":
#         # open the quotes collection
#         quotes_collection = quotes_db.quotes_collection
#         # insert the quote
#         quote_data = {"owner": user, "text": text, "author": author}
#         quotes_collection.insert_one(quote_data)
#     # usually do a redirect('....')
#     return redirect("/quotes")


# @app.route("/edit/<id>", methods=["GET"])
# def get_edit(id=None):
#     session_id = request.cookies.get("session_id", None)
#     if not session_id:
#         response = redirect("/login")
#         return response
#     if id:
#         # open the quotes collection
#         quotes_collection = quotes_db.quotes_collection
#         # get the item
#         data = quotes_collection.find_one({"_id": ObjectId(id)})
#         data["id"] = str(data["_id"])
#         return render_template("edit_quote.html", data=data)
#     # return to the quotes page
#     return redirect("/quotes")


# @app.route("/edit", methods=["POST"])
# def post_edit():
#     session_id = request.cookies.get("session_id", None)
#     if not session_id:
#         response = redirect("/login")
#         return response
#     _id = request.form.get("_id", None)
#     text = request.form.get("text", "")
#     author = request.form.get("author", "")
#     if _id:
#         # open the quotes collection
#         quotes_collection = quotes_db.quotes_collection
#         # update the values in this particular record
#         values = {"$set": {"text": text, "author": author}}
#         data = quotes_collection.update_one({"_id": ObjectId(_id)}, values)
#     # do a redirect('....')
#     return redirect("/quotes")


# @app.route("/delete", methods=["GET"])
# @app.route("/delete/<id>", methods=["GET"])
# def get_delete(id=None):
#     session_id = request.cookies.get("session_id", None)
#     if not session_id:
#         response = redirect("/login")
#         return response
#     if id:
#         # open the quotes collection
#         quotes_collection = quotes_db.quotes_collection
#         # delete the item
#         quotes_collection.delete_one({"_id": ObjectId(id)})
#     # return to the quotes page
#     return redirect("/quotes")
