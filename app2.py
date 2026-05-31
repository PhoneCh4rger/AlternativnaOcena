#pip install flask, pip install tinydb, python app2.py

from flask import Flask, render_template, request, redirect, session, jsonify
from tinydb import TinyDB, Query
from datetime import datetime

app = Flask(
    __name__,
    template_folder="templates2",
    static_folder="static2"
)

app.secret_key = "nekaj"

db = TinyDB("db.json")
users = db.table("users2")
objave = db.table("objave")
komentarji = db.table("komentarji")

User = Query()
Objava = Query()
Komentar = Query()


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
        username = request.form["username"]
        password = request.form["password"]
        if users.search(User.username == username):
            return render_template("register.html", napaka="Uporabnik že obstaja.")
        users.insert({"username": username, "password": password})
        return redirect("/login")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    vse_objave = []
    for o in objave.all():
        o_dict = dict(o)
        o_dict["doc_id"] = o.doc_id
        vse_objave.append(o_dict)
    return render_template("dashboard.html", user=session["user"], objave=vse_objave)

@app.route("/objavi", methods=["POST"])
def objavi():
    if "user" not in session:
        return redirect("/login")
    vsebina = request.form["vsebina"]
    objave.insert({
        "username": session["user"],
        "vsebina": vsebina,
        "cas": datetime.now().strftime("%d.%m.%Y %H:%M")
    })
    return redirect("/dashboard")


@app.route("/izbrisi_objavo", methods=["POST"])
def izbrisi_objavo():
    if "user" not in session:
        return redirect("/login")
    doc_id = int(request.form["doc_id"])
    objave.remove(doc_ids=[doc_id])
    komentarji.remove(Komentar.objava_id == doc_id)
    return redirect("/dashboard")


@app.route("/komentar/dodaj", methods=["POST"])
def dodaj_komentar():
    if "user" not in session:
        return jsonify({"napaka": "Nisi prijavljen"}), 401
    data      = request.get_json()
    objava_id = data["objava_id"]
    besedilo  = data["besedilo"]
    komentarji.insert({
        "objava_id": objava_id,
        "username":  session["user"],
        "besedilo":  besedilo
    })
    return jsonify({"ok": True, "username": session["user"], "besedilo": besedilo})


@app.route("/komentar/preberi/<int:objava_id>")
def preberi_komentarje(objava_id):
    if "user" not in session:
        return jsonify({"napaka": "Nisi prijavljen"}), 401
    rezultat = komentarji.search(Komentar.objava_id == objava_id)
    return jsonify(rezultat)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
