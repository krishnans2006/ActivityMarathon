from flask import Flask, render_template, redirect, url_for, request, session, flash
import csv


app = Flask(__name__)
app.config["SECRET_KEY"] = "hello"


def make_session_permanent():
    session.permanent = True


@app.route("/")
def home():
    return render_template("index.html", session=session)


@app.route("/login", methods=("GET", "POST"))
def login():
    if session.get("logged_in"):
        flash("0You are already logged in!")
        return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form.get("email")
        pwd = request.form.get("password")
        rme = request.form.get("rememberme")
        with open('data/accounts.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                if row[2] == email and row[3] == pwd:
                    session["logged_in"] = True
                    session["first_name"] = row[0]
                    session["last_name"] = row[1]
                    session["email"] = email
                    session["pwd"] = pwd
                    session["pts"] = row[4]
                    flash(f"1Successfully Logged In as {row[0]} {row[1]}!")
                    if rme:
                        make_session_permanent()
                    return redirect(url_for("home"))
        flash("0Incorrect Username or Password!")
        return redirect(url_for("login"))
    return render_template("login.html", session=session)


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("logged_in"):
        flash("0You are already logged in!")
        return redirect(url_for("home"))
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        pwd = request.form.get("password")
        with open('data/accounts.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                if row[2] == email:
                    flash(
                        "0You are already registered with this email! Please Log In or use another email."
                    )
                    return redirect(url_for("register"))
        with open('data/accounts.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([fname, lname, email, pwd, 0])
            flash("1Successfully Registered!")
            return redirect(url_for("login"))
    return render_template("register.html", session=session)


@app.route("/logout")
def logout():
    session.clear()
    flash("1You were successfully logged out!")
    return redirect(url_for("login"))


@app.route("/leaderboard")
def leaderboard():
    with open('data/accounts.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        sorted_by_pts = sorted(reader, key=lambda l: l[4], reverse=True)
    return render_template("leaderboard.html", leaderboard=sorted_by_pts)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
