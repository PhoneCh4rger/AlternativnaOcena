# pip install flask, pip install tinydb, pip install requests, python app3.py

from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query
import requests

app = Flask(
    __name__,
    template_folder="templates3",
    static_folder="static3"
)

app.secret_key = "noro_dober_kljuc"

TMDB_KEY = "1a26fd98d93c977021aa0bd6b150c234"
TMDB_URL = "https://api.themoviedb.org/3"

db = TinyDB("db.json")
users  = db.table("users3")
filmi  = db.table("filmi")

User  = Query()
Film  = Query()


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
        return render_template("login.html", napaka="Napačno ime ali geslo.")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username  = request.form["username"]
        password  = request.form["password"]
        vprasanje = request.form["vprasanje"]
        odgovor   = request.form["odgovor"]
        if users.search(User.username == username):
            return render_template("register.html", napaka="Uporabnik že obstaja.")
        users.insert({
            "username":  username,
            "password":  password,
            "vprasanje": vprasanje,
            "odgovor":   odgovor
        })
        return redirect("/login")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/pozabljeno", methods=["GET", "POST"])
def pozabljeno():
    if request.method == "POST":
        username = request.form["username"]
        user = users.get(User.username == username)

        if "odgovor" not in request.form or request.form["odgovor"] == "":
            if user:
                return render_template("pozabljeno.html", vprasanje=user["vprasanje"], username=username)
            return render_template("pozabljeno.html", napaka="Uporabnik ne obstaja.")

        odgovor = request.form["odgovor"]
        if user and user["odgovor"] == odgovor:
            session["reset_user"] = username
            return redirect("/novo_geslo")
        return render_template("pozabljeno.html", napaka="Napačen odgovor.", vprasanje=user["vprasanje"])

    return render_template("pozabljeno.html")


@app.route("/novo_geslo", methods=["GET", "POST"])
def novo_geslo():
    if "reset_user" not in session:
        return redirect("/login")
    if request.method == "POST":
        novo = request.form["geslo"]
        users.update(
            {"password": novo},
            User.username == session["reset_user"]
        )
        session.pop("reset_user") 
        return redirect("/login")
    return render_template("novo_geslo.html")



@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    filter = request.args.get("filter", "vse")
    if filter == "vse":
        moji_filmi = filmi.search(Film.username == session["user"])
    else:
        moji_filmi = filmi.search(
            (Film.username == session["user"]) &
            (Film.status == filter)
        )
    return render_template("dashboard.html", user=session["user"], filmi=moji_filmi, aktiven=filter)

@app.route("/isci")
def isci():
    if "user" not in session:
        return jsonify({"napaka": "Nisi prijavljen"}), 401
    poizvedba = request.args.get("q", "")
    odgovor = requests.get(f"{TMDB_URL}/search/movie", params={
        "api_key": TMDB_KEY,
        "query": poizvedba,
        "language": "sl-SI"
    })
    podatki = odgovor.json()
    rezultati = []
    for film in podatki.get("results", [])[:6]:
        rezultati.append({
            "tmdb_id": film["id"],
            "naslov":  film["title"],
            "opis":    film.get("overview", ""),
            "ocena":   film.get("vote_average", 0),
            "slika":   "https://image.tmdb.org/t/p/w200" + film["poster_path"] if film.get("poster_path") else ""
        })
    return jsonify(rezultati)


@app.route("/dodaj", methods=["POST"])
def dodaj():
    if "user" not in session:
        return redirect("/login")
    tmdb_id = int(request.form["tmdb_id"])
    obstaja = filmi.search(
        (Film.username == session["user"]) &
        (Film.tmdb_id == tmdb_id)
    )
    if not obstaja:
        filmi.insert({
            "username": session["user"],
            "tmdb_id":  tmdb_id,
            "naslov":   request.form["naslov"],
            "slika":    request.form["slika"],
            "ocena":    request.form["ocena"],
            "status":   "želim gledati" 
        })
    return redirect("/dashboard")


@app.route("/status", methods=["POST"])
def status():
    if "user" not in session:
        return redirect("/login")
    tmdb_id    = int(request.form["tmdb_id"])
    nov_status = request.form["status"]
    filmi.update(
        {"status": nov_status},
        (Film.username == session["user"]) &
        (Film.tmdb_id  == tmdb_id)
    )
    return redirect("/dashboard")


@app.route("/izbrisi", methods=["POST"])
def izbrisi():
    if "user" not in session:
        return redirect("/login")
    tmdb_id = int(request.form["tmdb_id"])
    filmi.remove(
        (Film.username == session["user"]) &
        (Film.tmdb_id  == tmdb_id)
    )
    return redirect("/dashboard")


app.run(debug=True, port=5000)