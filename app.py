import re
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- 1. CONFIGURATION ---
# Crée un chemin absolu pour la base de données SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'universite.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- 2. MODÈLE DE DONNÉES (La Structure) ---
class Etudiant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    tel = db.Column(db.String(20))

# Création de la base de données physique si elle n'existe pas
with app.app_context():
    db.create_all()

# --- 3. ROUTES POUR LES PAGES (HTML) ---

@app.route('/')
def index():
    """Page d'inscription (Formulaire)"""
    return render_template('inscription.html')

@app.route('/chatbot')
def chatbot_page():
    """Page de l'interface de discussion animée"""
    return render_template('chatbot.html')

@app.route('/liste')
def voir_liste():
    """Affiche tous les étudiants dans un tableau"""
    tous_les_etudiants = Etudiant.query.all()
    return render_template('liste.html', etudiants=tous_les_etudiants)

# --- 4. ROUTES POUR LA LOGIQUE (TRAITEMENT) ---

@app.route('/ajouter', methods=['POST'])
def ajouter_etudiant():
    """Enregistre un étudiant via le formulaire classique"""
    nom_form = request.form.get('nom')
    email_form = request.form.get('email')
    tel_form = request.form.get('tel')

    nouvel_etudiant = Etudiant(nom=nom_form, email=email_form, tel=tel_form)

    try:
        db.session.add(nouvel_etudiant)
        db.session.commit()
        return f"<h1>Succès ! {nom_form} a été ajouté.</h1><a href='/'>Retour</a>"
    except Exception as e:
        db.session.rollback()
        return "<h1>Erreur : Cet email existe déjà !</h1><a href='/'>Retour</a>"

# --- 5. ROUTES API (JSON / AJAX) ---

@app.route('/api/recherche')
def api_recherche():
    """API pour la recherche instantanée (barre de recherche)"""
    query = request.args.get('nom', '')
    resultats = Etudiant.query.filter(Etudiant.nom.contains(query)).all()
    
    output = []
    for e in resultats:
        output.append({"nom": e.nom, "email": e.email, "tel": e.tel})
    
    return jsonify(output)

@app.route('/api/chatbot', methods=['POST'])
def chatbot_logic():
    """Logique d'analyse de phrases pour le chatbot"""
    data = request.json
    message_utilisateur = data.get('message', '').lower()
    
    # Mots à retirer pour isoler le nom propre
    mots_cles = ["donne", "moi", "les", "informations", "sur", "qui", "est", "cherche", "infos", "de"]
    
    # On nettoie la phrase
    mots = re.sub(r'[^\w\s]', '', message_utilisateur).split() # Retire la ponctuation
    nom_trouve = ""
    for mot in mots:
        if mot not in mots_cles:
            nom_trouve = mot
            break

    # Recherche dans la base
    etudiant = Etudiant.query.filter(Etudiant.nom.contains(nom_trouve)).first()

    if etudiant and nom_trouve != "":
        reponse = f"J'ai trouvé ! Voici les infos pour <b>{etudiant.nom}</b> :<br>📧 Email: {etudiant.email}<br>📞 Tel: {etudiant.tel}"
    else:
        reponse = f"Désolé, je ne trouve aucune information pour '{nom_trouve}'."
    
    return jsonify({"reponse": reponse})

# --- LANCEMENT ---
if __name__ == '__main__':
    app.run(debug=True)