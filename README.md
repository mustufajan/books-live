# books-live

Tech stack: HTML | CSS | Python | PostgreSQL | SQLAlchemy | JSON | Flask

A Goodreads like book review website that allows users to access reviews made by other people, leave reviews for books, and make API calls to pull in data from Goodreads.

Key features:
Registration & login: Users should be able to register for your website, providing a username and password. Users should also be able to log in and log out of the website.

Search: Once a user has logged in, they should be taken to a page where they can search for a book. Users should be able to type in the ISBN number of a book, the title of a book, or the author of a book. After performing the search, the website should display a list of possible matching results, or some sort of message if there were no matches. If the user typed in only part of a title, ISBN, or author name, the search page should find matches for those as well

Book Page: When users click on a book from the results of the search page, they should be taken to a book page, with details about the book: its title, author, publication year, ISBN number, and any reviews that users have left for the book on the website.

Review Submission: On book page, users should be able to submit a review: consisting of a rating on a scale of 1 to 5, as well as a text component to the review where the user can write their opinion about a book. Users should not be able to submit multiple reviews for the same book.

Goodreads Review Data: On the book page, you should also display (if available) the average rating and number of ratings the work has received from Goodreads.

