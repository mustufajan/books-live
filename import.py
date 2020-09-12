import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

db.execute("CREATE TABLE authors(id SERIAL PRIMARY KEY NOT NULL, name TEXT NOT NULL)")
db.commit()
db.execute("CREATE TABLE books(id SERIAL PRIMARY KEY NOT NULL, ISBN TEXT NOT NULL, title TEXT NOT NULL, author_ID INTEGER REFERENCES authors , year INTEGER NOT NULL)")
db.commit()

with open('books.csv') as books:

    reader= csv.DictReader(books)

    for row in reader:

        author_name = db.execute("SELECT * FROM authors WHERE name=:name", { "name": row['author'].lower() })

        if author_name.rowcount == 0:
            db.execute("INSERT INTO authors(name) VALUES(:name)", {"name": row['author'].lower()})
            db.commit()

        author = db.execute("SELECT * FROM authors WHERE name=:name", { "name": row['author'].lower() } ).fetchone()

        db.execute("INSERT INTO books(ISBN, title, author_ID, year ) VALUES(:ISBN,:title,:author_ID ,:year)", 
                {"ISBN": row['isbn'].lower(), "title": row['title'].lower(), "author_ID": author.id, "year": row['year']})
        db.commit()

print("Import Successful!")
