
from flask import Flask, render_template, request, jsonify
import sqlite3
import datetime

# Connect to the SQLite database
# conn = sqlite3.connect('jeux.db')
# A répéter dans chaque fonction pour éviter de causer des erreurs

# Create a cursor object
# cur = conn.cursor()
# A répéter dans chaque fonction pour éviter de causer des erreurs
# Now you can use cur.execute() to run SQL commands, conn.commit() to save  changes, and conn.close() to save all changes

# Configure application
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def homepage():
    conn = sqlite3.connect('jeux.db')
    cur = conn.cursor()
    cur.execute("""SELECT name, image FROM jeux;""")
    data = cur.fetchall()
    conn.close()
    return render_template('homepage.html', data=data, show_bar = True)


@app.route('/search', methods=['GET', 'POST'])
def search():
    noresult = False
    searchBar = request.args.get('searchBar')
    conn = sqlite3.connect('jeux.db')
    cur = conn.cursor()
    cur.execute("""SELECT name, image FROM jeux WHERE name LIKE ?;""", ('%' + searchBar + '%',))
    data = cur.fetchall()
    conn.close()
    if not data:
        noresult = True
    return render_template('index.html', show_link=True, data=data, noresult=noresult, show_bar = True)

@app.route('/searchsuggestion', methods=['POST'])
def searchsuggestion():
    conn = sqlite3.connect('jeux.db')
    cur = conn.cursor()
    searchBarBis = request.json.get('searchBarBis', '')  # Get search term from JSON
    if searchBarBis != "":
        cur.execute("""SELECT name FROM jeux WHERE name LIKE ?;""", ('%' + searchBarBis + '%',))
        suggestiondata = cur.fetchall()
        conn.close()
        return jsonify(suggestiondata)  # Return JSON response
    else:
        conn.close()
        return jsonify([])  # Return empty list if search term is empty


@app.route('/jeu', methods=['GET', 'POST'])
def jeu():
    if request.method == "GET":
        name = request.args.get('name')
        conn = sqlite3.connect('jeux.db')
        cur = conn.cursor()
        cur.execute("""SELECT type, image, players, category, state, description FROM jeux WHERE name = ?;""",  (name,))
        data = cur.fetchone()
        conn.close()
        if data is None:
            return "No data found for the given name"
        empruntable = False
        nonempruntable = False
        emprunte = False
        state = str(data[4])
        if state == 'Empruntable':
            empruntable = True
        if state == 'Non Empruntable':
            nonempruntable = True
        if state == 'Emprunte':
            emprunte = True
        b = request.args.get('b') == 'B'
        return render_template('jeu.html', show_link=True, show_bar=True, name=name, data=data, b=b, empruntable=empruntable, nonempruntable=nonempruntable, emprunte=emprunte)

    elif request.method == "POST":
        typerequete = request.form.get('typerequete')
        if typerequete == "borrow":
            name = request.form.get('name')
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            fullname = firstname + ' ' + lastname
            fullname = fullname.replace("'", "''")
            current_date = datetime.datetime.today().strftime('%d-%m-%Y')
            state = 'Emprunte'
            conn = sqlite3.connect('jeux.db')
            cur = conn.cursor()
            cur.execute("""UPDATE jeux SET lastborrowed = ? WHERE name = ?;""",  (fullname, name))
            cur.execute("""UPDATE jeux SET date = ? WHERE name = ?;""",  (current_date, name))
            cur.execute("""UPDATE jeux SET state = ? WHERE name = ?;""",  (state, name))
            conn.commit()
            cur.execute("""SELECT type, image, players, category, state, description FROM jeux WHERE name = ?;""",  (name,))
            data = cur.fetchone()
            conn.close()
            if data is None:
                return "No data found for the given name"
            empruntable = False
            nonempruntable = False
            emprunte = True
            return render_template('jeu.html', show_link=True, show_bar=True, name=name, data=data, b=True, empruntable=empruntable, nonempruntable=nonempruntable, emprunte=emprunte)
        elif typerequete == "return":
            state = 'Empruntable'
            name = request.form.get('name')
            current_date = datetime.datetime.today().strftime('%d-%m-%Y')
            conn = sqlite3.connect('jeux.db')
            cur = conn.cursor()
            cur.execute("""UPDATE jeux SET date = ? WHERE name = ?;""",  (current_date, name))
            cur.execute("""UPDATE jeux SET state = ? WHERE name = ?;""",  (state, name))
            conn.commit()
            cur.execute("""SELECT type, image, players, category, state, description FROM jeux WHERE name = ?;""",  (name,))
            data = cur.fetchone()
            conn.close()
            if data is None:
                return "No data found for the given name"
            empruntable = True
            nonempruntable = False
            emprunte = False
            return render_template('jeu.html', show_link=True, show_bar=True, name=name, data=data, b=True, empruntable=empruntable, nonempruntable=nonempruntable, emprunte=emprunte)
    return "Invalid request method"

@app.route('/administrateur', methods=['GET', 'POST'])
def administrateur():
    if (request.method == "POST"):
        typerequete = request.form.get('typerequete')
        if typerequete == "add":
            return add()
        if typerequete == "modify":
            return modify()
        if typerequete == "remove":
            return remove()
        if typerequete == "lastborrowed":
            return lastborrowed()
    return render_template('administrateur.html', show_link=True, show_bar=False, announcement=False, text=" ")


# Créer la table avec la commande
# CREATE TABLE jeux (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, name TEXT, image TEXT, players TEXT, category TEXT, state TEXT, lastborrowed TEXT);
# Comme ça pas besoin de créer un nouvel id dans la fonction python, il s'autoincrémente
@app.route('/administrateur', methods=['GET', 'POST'])
def add():
    conn = sqlite3.connect('jeux.db')
    cur = conn.cursor()
    name = request.form.get('namea')
    name = name.replace("'", "''")
    type = request.form.get('typea')
    type = type.replace("'", "''")
    image = request.form.get('imagea')
    image = image.replace("'", "''")
    players = request.form.get('playersa')
    players = players.replace("'", "''")
    category = request.form.get('categorya')
    category = category.replace("'", "''")
    state = request.form.get('statea')
    state = state.replace("'", "''")
    description = request.form.get('descriptiona')
    description = description.replace("'", "''")
    cur.execute("""INSERT INTO jeux(type, name, image, players, category, state, lastborrowed, description, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL);""", (type, name, image, players, category, state, description, None))
    conn.commit()
    conn.close()
    text = "Le jeu a bien été ajouté"
    return render_template('administrateur.html', show_bar=False, show_link=True, text=text, announcement=True)


@app.route('/administrateur', methods=['GET', 'POST'])
def modify():
    conn = sqlite3.connect('jeux.db')
    cur = conn.cursor()
    originalname = request.form.get('originalname')
    originalname = originalname.replace("'", "''")
    name = request.form.get('namem')
    name = name.replace("'", "''")
    type = request.form.get('typem')
    type = type.replace("'", "''")
    image = request.form.get('imagem')
    image = image.replace("'", "''")
    players = request.form.get('playersm')
    players = players.replace("'", "''")
    category = request.form.get('categorym')
    category = category.replace("'", "''")
    state = request.form.get('statem')
    state = state.replace("'", "''")
    description = request.form.get('descriptionm')
    description.replace("'", "''")
    cur.execute("""SELECT * FROM jeux WHERE name = ?;""", (originalname,))
    rows = cur.fetchall()
    if rows:
        if type:
            cur.execute("""UPDATE jeux SET type = ? WHERE name = ?;""", (type, originalname))
            conn.commit()
        if image:
            cur.execute("""UPDATE jeux SET image = ? WHERE name = ?;""", (image, originalname))
            conn.commit()
        if players:
            cur.execute("""UPDATE jeux SET players = ? WHERE name = ?;""", (players, originalname))
            conn.commit()
        if description:
            cur.execute("""UPDATE jeux SET description = ? WHERE name = ?;""", (description, originalname))
            conn.commit()
        if category:
            cur.execute("""UPDATE jeux SET category = ? WHERE name = ?;""",
                        (category, originalname))
            conn.commit()
        if state:
            cur.execute("""UPDATE jeux SET state = ? WHERE name = ?;""", (state, originalname))
            conn.commit()
        if name:
            cur.execute("""UPDATE jeux SET name = ? WHERE name = ?;""", (name, originalname))
            conn.commit()
        conn.close()
        text = "Le jeu est bien modifié dans la base de données"
        return render_template('administrateur.html', show_bar=False, show_link=True, text=text, announcement=True)
    else:
        conn.close()
        text = "Le jeu n'est pas initialement dans la base de données"
        return render_template('administrateur.html', show_bar=False, show_link=True, text=text, announcement=True)


@app.route('/administrateur', methods=['GET', 'POST'])
def remove():
    conn = sqlite3.connect('jeux.db')
    cur = conn.cursor()
    name = request.form.get('namer')
    name = name.replace("'", "''")
    cur.execute("""SELECT * FROM jeux WHERE name = ?;""", (name,))
    rows = cur.fetchall()
    if rows:
        cur.execute("""DELETE FROM jeux WHERE name = ?;""", (name,))
        conn.commit()
        conn.close()
        text = "Le jeu est bien supprimé"
        return render_template('administrateur.html', show_link=True, show_bar=False, text=text, announcement=True)
    else:
        conn.close()
        text = "Le jeu n'existe pas dans la base de données"
        return render_template('administrateur.html', show_link=True, show_bar=False, text=text, announcement=True)


@app.route('/administrateur', methods=['GET', 'POST'])
def lastborrowed():
    conn = sqlite3.connect('jeux.db')
    cur = conn.cursor()
    name = request.form.get('namel')
    name = name.replace("'", "''")
    cur.execute("""SELECT lastborrowed, date, state FROM jeux WHERE name = ?;""", (name,))
    rows = cur.fetchone()
    conn.close()
    if rows:
        if rows[2] == 'Non Empruntable':
            text = "Le jeu devrait être en salle troll. Il n'est pas empruntable"
            return render_template('administrateur.html', show_bar=False, show_link=True, text=text, announcement=True)
        if rows[2] == 'Empruntable':
            if rows[0] is None or rows[1] is None:
                text = "Le jeu devrait être en salle troll"
                return render_template('administrateur.html', show_bar=False, show_link=True, text=text, announcement=True)
            else:
                text = "Le dernier emprunt a  été effectué par {} et le jeu aurait été rendu le {}".format(rows[0], rows[1])
                return render_template('administrateur.html', show_bar=False, show_link=True, text=text, announcement=True)
        if rows[2] == 'Emprunte':
            text = "Le jeu a été emprunté par {} le {}".format(rows[0], rows[1])
            return render_template('administrateur.html', show_link=True, show_bar=False, text=text, announcement=True)
    else:
        text = "Le jeu n'est pas dans la base de données"
        return render_template('administrateur.html', show_link=True, show_bar=False, text=text, announcement=True)
