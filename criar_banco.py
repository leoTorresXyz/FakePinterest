from luckyowee import database, app
from luckyowee.models import Usuario, Foto

with app.app_context():
    database.create_all()