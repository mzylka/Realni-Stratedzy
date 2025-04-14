from app import db
import os
from app.models import Post, Community, Game  # Zmień na swoją nazwę modelu
from flask import Flask
from config import config
from app.helpers import save_resized_image
 

# Jeśli korzystasz z aplikacji Flask, musisz ją wczytać przed operacjami na bazie danych
 
app = Flask(__name__)
app.config.from_object(config["development"])  # Załaduj odpowiednią konfigurację bazy danych
db.init_app(app)
with app.app_context():  # Tworzymy kontekst aplikacji
    # Pobranie wszystkich rekordów
    posts = db.session.execute(db.select(Post)).scalars()
    for post in posts:
        if post.thumb_name_min:
            try:
                file = open(os.path.join(app.config['UPLOAD_FOLDER_ABS'], f'thumbnails', post.thumb_name), 'rb')
            except OSError:
                print("File not found")
                continue
            split_name = post.thumb_name.split(".")
            name_min = split_name[0] + "_min." + split_name[1]
            print(name_min)
            save_resized_image(file, "thumbnail", name_min)
            print("Saved " + name_min)
 
    games = db.session.execute(db.select(Game)).scalars()
 
    for game in games:
        if game.thumb_name_min:
            try:
                file = open(os.path.join(app.config['UPLOAD_FOLDER_ABS'], f'logos', game.thumb_name), 'rb')
            except OSError:
                print("File not found")
                continue
            split_name = game.thumb_name.split(".")
            name_min = split_name[0] + "_min." + split_name[1]
            save_resized_image(file, "logo", name_min)
            print("Saved " + name_min)
 
    communities = db.session.execute(db.select(Community)).scalars()
 
    for c in communities:
        if c.thumb_name_min:
            try:
                file = open(os.path.join(app.config['UPLOAD_FOLDER_ABS'], f'logos', c.thumb_name), 'rb')
            except OSError:
                print("File not found")
                continue
            split_name = c.thumb_name.split(".")
            name_min = split_name[0] + "_min." + split_name[1]
            save_resized_image(file, "logo", name_min)
            print("Saved " + name_min)
 

print("Aktualizacja zakończona!")