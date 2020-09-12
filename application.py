import os
import hashlib
import requests
from flask import Flask, session, render_template, request, redirect
from flask_session.__init__ import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))





#login required function
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#apology function
def apology(message,code):
   return render_template("apology.html",message=message,code=code)


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
   if request.method=="POST":

       search_results=db.execute("SELECT * FROM books JOIN authors ON authors.id=books.author_id WHERE title LIKE :search_text  OR isbn LIKE :search_text OR name LIKE :search_text", 
                                {"search_text":'%'+request.form.get("search_text").lower()+'%'}).fetchall()


       return render_template("search_results.html", search_results=search_results) 

   return render_template("search.html")


@app.route("/review", methods=["GET", "POST"])
@login_required
def review():

    book = session.get('book')
    author=session.get('author')
    user=session.get('user')

    rating=1
    reviews = db.execute("SELECT * FROM reviews WHERE book_id=:book_id",{"book_id":book.id}).fetchall()

    # Goodreads API set up
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "MHvTyS4H8JHxEfSr0MImOQ", "isbns": book.isbn})
    result=res.json()

    if request.method == 'POST':

        if request.form.get('1'):
            rating=1
        if request.form.get('2'):
            rating=2
        if request.form.get('3'):
            rating=3
        if request.form.get('4'):
            rating=4
        if request.form.get('5'):
            rating=5
        
        review_number = db.execute("SELECT * FROM reviews WHERE reviewer=:reviewer AND book_ID=:book_ID",{"reviewer":session.get('user_id'), "book_ID":book.id}).fetchone()

        review_count = db.execute("SELECT COUNT(*) FROM reviews WHERE book_id=:book_id",{"book_id":book.id}).fetchone()[0]
        rating_total = db.execute("SELECT SUM(rating) FROM reviews WHERE book_id=:book_id",{"book_id":book.id}).fetchone()[0]
        

        if review_number is None:
            db.execute("INSERT into reviews (book_id,review,rating,reviewer) VALUES(:book_id,:review,:rating,:reviewer)", 
                        {"book_id":book.id,"review":request.form.get('review'),"rating": rating, "reviewer": user.id})
            db.commit()

            reviews = db.execute("SELECT * FROM reviews WHERE book_id=:book_id",{"book_id":book.id}).fetchall()
            return render_template("bookpage.html",book=book, author=author, reviews=reviews, result=result, review_count=review_count, rating_total=rating_total)

        else:
            return apology("You have already submitted a review for this book, thank you!", 403)

    return render_template("review.html", book=book, author=author, reviews=reviews)

@app.route("/<string:isbn>")
@login_required
def bookpage(isbn):

    book=db.execute("SELECT * FROM books WHERE isbn=:isbn", 
                                {"isbn":isbn}).fetchone()

    author=db.execute("SELECT * FROM authors WHERE authors.id=:author_id", 
                                {"author_id":book.author_id}).fetchone()
    
    
    reviews = db.execute("SELECT * FROM reviews WHERE book_id=:book_id",{"book_id":book.id}).fetchall()
    review_count = db.execute("SELECT COUNT(*) FROM reviews WHERE book_id=:book_id",{"book_id":book.id}).fetchone()[0]
    rating_total = db.execute("SELECT SUM(rating) FROM reviews WHERE book_id=:book_id",{"book_id":book.id}).fetchone()[0]



    print(review_count)
    print(rating_total)

    # Goodreads API set up
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "MHvTyS4H8JHxEfSr0MImOQ", "isbns": isbn})
    result=res.json()
    
    
    session['book']=book
    session['author']=author
    return render_template("bookpage.html", book=book, author=author, reviews=reviews, result=result, review_count=review_count, rating_total=rating_total)

@app.route("/register", methods=["GET", "POST"])
def registration():
   # Forget any user_id
   session.clear()
   
   if request.method=="POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation of password", 403)

        # Ensure password and confirmation matches
        if not request.form.get("password") == request.form.get("confirmation"):
            return apology("Passwords do not match", 403)

        # Query database for username
        user = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchone()
        
        # Ensure username exists and password is correct
        if not user is None:
            return apology("Username already exists", 403)
 
        # INSERT new user into the user database
        db.execute("INSERT INTO users (username, key) VALUES(:username,:key)", {"username": request.form.get("username"), "key": generate_password_hash(request.form.get("password"))})
        db.commit()

        # Query database for username
        user = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchone()

        # Remember which user has logged in
        session["user_id"] = user['id']
        session['user']=user

        # Redirect user to home page
        return redirect("/")

   else:   
      return render_template("registration.html")

@app.route("/login", methods=["GET", "POST"])
def login():
   if request.method=="POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        user = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchone()
        
        # Ensure username exists and password is correct
        if user is None or not check_password_hash(user['key'], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user['id']
        session['user']=user

        # Redirect user to home page
        return redirect("/")

   else:   
      return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")      