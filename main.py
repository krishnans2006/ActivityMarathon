from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_mail import Mail, Message
from replit import db
from datetime import timedelta

app = Flask(__name__)

app.config["SECRET_KEY"] = "fsediwq3e78fwshdore"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'activity.marathon@gmail.com'
app.config['MAIL_PASSWORD'] = db["account_pwd"]
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


def set_session_timeout(remember):
    session.permanent = True
    if remember:
        app.permanent_session_lifetime = timedelta(days=20)
    else:
        app.permanent_session_lifetime = timedelta(minutes=20)
    session.modified = True


@app.before_first_request
def populate_db():
    if not db.get("accounts"):
        db["accounts"] = []


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
        for user in db["accounts"]:
            if user["email"] == email and user["pwd"] == pwd:
                session["logged_in"] = True
                session["fname"] = user["fname"]
                session["lname"] = user["lname"]
                session["email"] = email
                session["pwd"] = pwd
                session["pts"] = user["pts"]
                flash(
                    f"1Successfully Logged In as {session['fname']} {session['lname']}!"
                )
                set_session_timeout(rme)
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
        for user in db["accounts"]:
            if user["email"] == email:
                flash(
                    "0You are already registered with this email! Please Log In or use another email."
                )
                return redirect(url_for("register"))
        db["accounts"] = db["accounts"] + [{
            "fname": fname,
            "lname": lname,
            "email": email,
            "pwd": pwd,
            "pts": 0
        }]
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
    sorted_by_pts = sorted(
        db["accounts"], key=lambda l: l["pts"], reverse=True)
    return render_template("leaderboard.html", leaderboard=sorted_by_pts)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        msg = Message(
            'New Video to Review!',
            sender=app.config['MAIL_USERNAME'],
            recipients=['activity.marathon.approve1@gmail.com'])
        msg.body = f"Hello Admin! You have a new video to review! {session['fname']} {session['lname']} has submitted their daily video!"
        msg.attach("video.mp4", "video/mp4", file.read())
        mail.send(msg)
        flash("1File was sent to review successfully!")
        return redirect(url_for("leaderboard"))
    return render_template("upload.html")


@app.route("/shop", methods=["GET", "POST"])
def shop():
    return render_template("shop.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
