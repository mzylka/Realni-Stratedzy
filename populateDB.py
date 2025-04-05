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
        if not post.thumb_name_min:
            try:
                file = open(os.path.join(app.config['UPLOAD_FOLDER_ABS'], f'thumbnails', post.thumb_name), 'rb')
            except OSError:
                print("File not found")
                continue
            split_name = post.thumb_name.split(".")
            name_min = split_name[0] + "_min." + split_name[1]
            print(name_min)
            save_resized_image(file, "thumbnail", name_min)
            post.thumb_name_min = name_min
            db.session.add(post)
            print("Saved " + name_min)

    db.session.commit()  # Zapisujemy zmiany

    games = db.session.execute(db.select(Post)).scalars()
    for game in games:
        if not game.thumb_name_min:
            try:
                file = open(os.path.join(app.config['UPLOAD_FOLDER_ABS'], f'logos', game.thumb_name), 'rb')
            except OSError:
                print("File not found")
                continue
            split_name = game.thumb_name.split(".")
            name_min = split_name[0] + "_min." + split_name[1]
            save_resized_image(file, "logo", name_min)
            game.thumb_name_min = name_min
            db.session.add(game)
            print("Saved " + name_min)

    db.session.commit()

    communities = db.session.execute(db.select(Community)).scalars()
    for c in communities:
        if not c.thumb_name_min:
            try:
                file = open(os.path.join(app.config['UPLOAD_FOLDER_ABS'], f'logos', c.thumb_name), 'rb')
            except OSError:
                print("File not found")
                continue
            split_name = c.thumb_name.split(".")
            name_min = split_name[0] + "_min." + split_name[1]
            save_resized_image(file, "logo", name_min)
            c.thumb_name_min = name_min
            db.session.add(c)
            print("Saved " + name_min)

    db.session.commit()

print("Aktualizacja zakończona!")
