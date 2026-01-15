import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 1. Utilisation d'un fichier local permanent
# Le fichier universite.db sera créé dans le même dossier
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'universite.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 2. Modèle de données (Comme ta struct en C)
class Etudiant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True)

# 3. Script de test de persistance
def run_storage_test():
    with app.app_context():
        # Création de la base physique
        db.create_all()
        
        # Ajout d'un étudiant pour le test
        nom_test = "Homilus_Admin"
        etudiant_existe = Etudiant.query.filter_by(nom=nom_test).first()

        if not etudiant_existe:
            nouveau = Etudiant(nom=nom_test, email="admin@uni.edu")
            db.session.add(nouveau)
            db.session.commit()
            print(f"✨ Succès : '{nom_test}' a été enregistré dans le fichier.")
        else:
            print(f"ℹ️ Info : '{nom_test}' est déjà présent dans le stockage.")

        # Vérification du fichier
        if os.path.exists(os.path.join(basedir, 'universite.db')):
            size = os.path.getsize(os.path.join(basedir, 'universite.db'))
            print(f"💾 Fichier 'universite.db' détecté ({size} octets).")
            print("✅ TEST DE STOCKAGE RÉUSSI : Tes données sont en sécurité sur le disque.")

if __name__ == "__main__":
    run_storage_test()