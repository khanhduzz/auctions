import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Get information from database
    stocks = db.execute(
        "SELECT * FROM purchases WHERE username_id = ?", session["user_id"]
    )
    cash = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    money = 0

    # Update table through stocks
    for stock in stocks:
        price = lookup(stock["symbol"])
        db.execute(
            "UPDATE purchases SET price = ?, total = ? WHERE symbol = ?",
            price["price"],
            stock["amount"] * price["price"],
            stock["symbol"],
        )
        money += stock["amount"] * price["price"]

    # Get the data again
    stocks = db.execute(
        "SELECT * FROM purchases WHERE username_id = ?", session["user_id"]
    )

    # Update money for each user
    userMoney = db.execute(
        "SELECT * FROM money WHERE username_id = ?", session["user_id"]
    )
    if len(userMoney) < 1:
        db.execute(
            "INSERT INTO money(username_id, total) VALUES (?, ?)",
            session["user_id"],
            money,
        )
    else:
        db.execute(
            "UPDATE money SET total = ? WHERE username_id = ?",
            money,
            session["user_id"],
        )

    # Calculate the total
    totalFinal = cash[0]["cash"] + money

    # Check if stock != None
    if stocks != None:
        return render_template(
            "index.html",
            stocks=stocks,
            cash=cash[0],
            money=money,
            totalFinal=totalFinal,
        )

    return render_template("index.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # Check method
    if request.method == "POST":
        # Check if symbol is correct or not
        symbol = lookup(request.form.get("symbol"))
        if not symbol:
            return apology("Invalid symbol", 400)
        elif (
            not request.form.get("shares").isdigit()
            or not request.form.get("shares").isnumeric()
        ):
            return apology("Invalid shares", 400)
        elif int(request.form.get("shares")) < 1:
            return apology("Shares must greater than 1", 400)

        # Get amount from databse
        cash = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Calculate the total buy amount
        amount = int(request.form.get("shares")) * float(symbol["price"])

        # Check available cash or not
        if cash[0]["cash"] < amount:
            return apology("Do not enough cash", 400)
        else:
            # Calculate the left amount
            odd = cash[0]["cash"] - amount

            db.execute(
                "UPDATE users SET cash = ? WHERE id = ?", odd, session["user_id"]
            )

            userAmount = db.execute(
                "SELECT * FROM purchases WHERE username_id = ? AND symbol = ?",
                session["user_id"],
                symbol["symbol"],
            )

            if len(userAmount) < 1:
                db.execute(
                    "INSERT INTO purchases(username_id, symbol, amount, total, price, name) VALUES (?, ?, ?, ?, ?, ?)",
                    session["user_id"],
                    symbol["symbol"],
                    int(request.form.get("shares")),
                    amount * (float)(symbol["price"]),
                    symbol["price"],
                    symbol["name"],
                )
            else:
                totalAmount = userAmount[0]["amount"] + int(request.form.get("shares"))
                totalPrice = totalAmount * float(symbol["price"])
                db.execute(
                    "UPDATE purchases SET amount = ?, total = ?, price = ? WHERE username_id = ? AND symbol = ?",
                    totalAmount,
                    totalPrice,
                    symbol["price"],
                    session["user_id"],
                    symbol["symbol"],
                )

            db.execute(
                "INSERT INTO histories(username_id, symbol, amount, orderTime, price) VALUES(?, ?, ?, ?, ?)",
                session["user_id"],
                symbol["symbol"],
                int(request.form.get("shares")),
                datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                float(symbol["price"]),
            )
            flash("Bought")
            return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Get data from database
    stocks = db.execute(
        "SELECT * FROM histories WHERE username_id = ?", session["user_id"]
    )

    return render_template("/history.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Welcome")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # Check method
    if request.method == "POST":
        # Check if pick a invalid number
        if not request.form.get("symbol"):
            return apology("Invalid symbol", 400)

        # Get symbol from user
        quote = lookup(request.form.get("symbol"))

        if not quote:
            return apology("Invalid symbol", 400)
        else:
            return render_template("quote2.html", quote=quote)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget user
    session.clear()

    # Check Get method
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must choose a username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must enter a password", 400)

        # Ensure password confirmation is correct
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password do not match", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Check user exist
        if len(rows) == 1:
            return apology("User already exist!", 400)

        # Insert into database
        db.execute(
            "INSERT INTO users(username, hash) VALUES (?, ?)",
            request.form.get("username"),
            generate_password_hash(request.form.get("password")),
        )

        # Get data and logging again
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Register Successful")
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # Get all the symbol which user had
    stocks = db.execute(
        "SELECT * FROM purchases WHERE username_id = ?", session["user_id"]
    )

    # Check method
    if request.method == "POST":
        # Get symbol and amount
        symbol = lookup(request.form.get("symbol"))
        amount = (int)(request.form.get("shares"))

        # Check in database
        userSymbol = db.execute(
            "SELECT * FROM purchases WHERE username_id = ? AND symbol = ?",
            session["user_id"],
            symbol["symbol"],
        )

        if len(userSymbol) < 1 or userSymbol[0]["amount"] < amount:
            return apology("Do not enough shares", 400)
        else:
            odd = userSymbol[0]["amount"] - amount

            if odd == 0:
                db.execute(
                    "DELETE FROM purchases WHERE symbol = ? and username_id = ?",
                    symbol["symbol"],
                    session["user_id"],
                )
            else:
                db.execute(
                    "UPDATE purchases SET amount = ? WHERE username_id = ? AND symbol = ?",
                    odd,
                    session["user_id"],
                    symbol["symbol"],
                )

            # Calculate cash:
            cash = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

            cash[0]["cash"] = (int)(cash[0]["cash"]) + amount * float(symbol["price"])

            db.execute(
                "UPDATE users SET cash = ? WHERE id = ?",
                cash[0]["cash"],
                session["user_id"],
            )

            amount = (int)(0 - amount)
            db.execute(
                "INSERT INTO histories(username_id, symbol, amount, orderTime, price) VALUES(?, ?, ?, ?, ?)",
                session["user_id"],
                symbol["symbol"],
                amount,
                datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                float(symbol["price"]),
            )

            flash("Sold")
            return redirect("/")
    else:
        return render_template("sell.html", stocks=stocks)


@app.route("/changepwd", methods=["GET", "POST"])
@login_required
def changepwd():
    if request.method == "POST":
        # Get old password from databse:
        pwd = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Check typed in password correct or not
        typepwd = request.form.get("password")

        if not check_password_hash(pwd[0]["hash"], typepwd):
            return apology("Password incorrect!", 403)
        elif check_password_hash(pwd[0]["hash"], request.form.get("new_password")):
            return apology("Password must not the same", 403)
        elif request.form.get("new_password") != request.form.get("confirmation"):
            return apology("Password not match", 403)
        else:
            db.execute(
                "UPDATE users SET hash = ? WHERE id = ?",
                generate_password_hash(request.form.get("new_password")),
                session["user_id"],
            )
            flash("Password changed!")
            return redirect("/")

    return render_template("/changepwd.html")
