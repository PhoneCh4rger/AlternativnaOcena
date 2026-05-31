#pip install flask, pip install tinydb, python app1.py

from flask import Flask, render_template, request, redirect, session
from tinydb import TinyDB, Query

app = Flask(
    __name__,
    template_folder="templates1",
    static_folder="static1"
)

app.secret_key="7_eur_down_the_drain_zaigrcokeronemormigrt"

db= TinyDB("db.json")
users = db.table("users")
zapiski = db.table("zapiski")

User = Query()
Zapisek = Query()

@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users.get(User.username == username)
        if user and user["password"] == password:
            session["user"] = username
            return redirect("/dashboard")
        return "Napačno uporabniško ime ali geslo."
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.search(User.username == username):
            return "Uporabnik že obstaja."
        users.insert({"username": username, "password": password})
        return redirect("/login")
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    kategorija = request.args.get("kategorija", "vse") 
    if kategorija == "vse":
        moji_zapiski = zapiski.search(Zapisek.username == session["user"])
    else:
        moji_zapiski = zapiski.search(
            (Zapisek.username == session["user"]) &
            (Zapisek.kategorija == kategorija)
        )
    return render_template("dashboard.html", user=session["user"], zapiski=moji_zapiski, aktivna=kategorija)

@app.route("/dodaj", methods=["POST"])
def dodaj():
    if "user" not in session:
        return redirect("/login")
    naslov = request.form["naslov"]
    vsebina = request.form["vsebina"]
    kategorija = request.form["kategorija"]
    zapiski.insert({"username": session["user"], "naslov": naslov, "vsebina": vsebina, "kategorija": kategorija})
    return redirect("/dashboard")



@app.route("/izbrisi", methods=["POST"])
def izbrisi():
    if "user" not in session:
        return redirect("/login")
    naslov = request.form["naslov"]
    zapiski.remove((Zapisek.username == session["user"]) & (Zapisek.naslov == naslov))
    return redirect("/dashboard")

@app.route("/uredi", methods=["POST"])
def uredi():
    if "user" not in session:
        return redirect("/login")
    stari_naslov = request.form["stari_naslov"]
    nov_naslov = request.form["naslov"]
    nova_vsebina = request.form["vsebina"]
    nova_kat= request.form["kategorija"]
    zapiski.update(
        {"naslov": nov_naslov, "vsebina": nova_vsebina, "kategorija": nova_kat}, 
        (Zapisek.username == session["user"]) & (Zapisek.naslov == stari_naslov)
    )
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

app.run(debug=True)