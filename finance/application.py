import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    a = ""
    bgg = db.execute("SELECT * FROM stocks WHERE id = ?", session["user_id"])
    if len(bgg) < 1:
        a = "nao tienes aciones my friend"

        # protoitpo para caso eu queira mostrar o preço em tempo real
        # for n in bgg[0]["name"]:
            # bgg[0]["price"] = usd(bgg[0]["price"])
            # dale = lookup(bgg[0]["name"])
            # bgg[0]["now"] = dale["name"]
    # else:
    money = db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])
    return render_template("index.html", a = a, data = bgg, ala= usd(money[0]["cash"]))

@app.route("/buy", methods=["GET", "POST"])
#@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        if lookup(request.form.get("stock")) == None or not int(request.form.get('quantity')):
            return render_template("buy.html", situation="papakil")
        else:
            rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
            dale = lookup(request.form.get("stock"))
            malote = rows[0]["cash"]
            admita = int(request.form.get('quantity'))
            preco = float(dale["price"])
            if (admita * int(dale["price"])) > malote:
                return render_template("buy.html", situation="pobre")
            else:
                if len(db.execute("SELECT * FROM stocks WHERE name = ?", dale["name"]))  == 1:
                    old = db.execute("SELECT * FROM stocks WHERE name = ?", dale["name"])
                    dalii = old[0]["amount"] + admita
                    precin = (((old[0]["price"] * old[0]["amount"]) + preco * admita))/dalii
                    db.execute("UPDATE stocks SET price = ?, amount = ?, id = ?, sprice = ? WHERE name = ?", precin, dalii, old[0]["id"], usd(precin), dale["name"])
                    db.execute("INSERT INTO historyc VALUES( ?, ?, ?, -?, ?, ?)", dale["name"], usd(preco), dale["symbol"], usd(admita * preco), "compra", old[0]["id"])
                    db.execute("UPDATE users SET cash = ?", malote - (admita * dale["price"]))
                    return render_template("buy.html", situation="parabens minha fera")
                else:
                    db.execute("INSERT INTO stocks VALUES( ?, ?, ?, ?, ?, ?)", dale["name"], preco, dale["symbol"], admita, rows[0]["id"], usd(preco))
                    db.execute("INSERT INTO historyc VALUES( ?, ?, ?, -?, ?, ?)", dale["name"], usd(preco), dale["symbol"], usd(admita * preco), "compra", rows[0]["id"])
                    return render_template("buy.html", situation="parabens favelado")
    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    #a msm coisa do index
    bgg = db.execute("SELECT * FROM historyc WHERE id = ?", session["user_id"])
    return render_template("history.html", data = bgg)


    return apology("TODO")


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
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
#@login_required
def quote():
    if request.method == "POST":
        if lookup(request.form.get("stock")) == None:
            return render_template("quote.html", dali = "Esse simbolo nao existe")
        else:
            dale = lookup(request.form.get("stock"))
            return render_template("quoted.html", Name = dale['name'], Price = dale['price'], Symbol = dale['symbol'])

    else:
        return render_template("quote.html")
#  pk_1bf3bca2023f48fabfda376efc4c7dbc
 # pk_64c9155bd5ba40f29ef8905003bdb86d
  #key pk_0596a81751184edca5826f0b98b8a74b
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()
    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) == 1:
            return apology("This username is arealdy in use")
        if len(rows) != 1:
            #hash = request.form.get("password")
            db.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", request.form.get("username"), generate_password_hash(request.form.get("password")))

            return redirect("/")
    else:
        return render_template("register.html")

    #return redirect("/login")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        #        highlight
        dalin = db.execute("SELECT * FROM stocks WHERE id= ? and symbol = ?", session["user_id"], request.form.get("stock"))
        #  favelado n tiver a açao
        if len(dalin) == 0:
            return render_template("sell.html", admitad= "vc n tienes esta acion")
        else:
            # Mais acao q o possivel
            pressao = float(dalin[0]["amount"])
            toti = float(request.form.get("quantity"))
            if toti > pressao:
                return render_template("sell.html", admitad= "éobesta")
            else:
                # finalizar a compra
                admita = int(request.form.get('quantity'))
                precoa = lookup(request.form.get("stock"))
                rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
                preco = float(precoa["price"])
                malote = rows[0]["cash"]
                if toti == pressao:
                    # vende/exclui tudo
                    db.execute("DELETE FROM stocks WHERE name = ?", dalin[0]["name"])
                    db.execute("INSERT INTO historyc VALUES( ?, ?, ?, +?, ?, ?)", dalin[0]["name"], usd(preco), dalin[0]["symbol"], usd(toti * preco), "venda", rows[0]["id"])
                    db.execute("UPDATE users SET cash = ?", malote + (admita * preco))
                    return redirect("/")
                else:
                    # vende/exclui parte
                    db.execute("UPDATE stocks WHERE name = ? SET price=? sprice=? amount=?", dalin[0]["name"], preco, usd(preco), admita)
                    db.execute("INSERT INTO historyc VALUES( ?, ?, ?, +?, ?, ?)", dalin[0]["name"], usd(preco), dalin[0]["symbol"], usd(toti * preco), "venda", rows[0]["id"])
                    db.execute("UPDATE users SET cash = ?", malote + (admita * preco))
                    return redirect("/")
    else:
        return render_template("sell.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# TRUNCATE TABLE tabelaname;
# DROP TABLE stocks;
# CREATE TABLE stocks(name varchar(255), price FLOAT, symbol varchar(255), amount INTENGER, id INTENGER, FOREIGN KEY(id) REFERENCES users(id)));
# CREATE TABLE historyc(name varchar(255), price FLOAT, symbol varchar(255), result varchar(255), tipe varchar(255), id INTENGER, FOREIGN KEY(id) REFERENCES users(id));
# INSERT INTO stocks VALUES(dale[0], dale[1], dale[3], )