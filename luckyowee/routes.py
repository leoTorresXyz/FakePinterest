from flask import render_template, url_for, redirect
from luckyowee import app, database, bcrypt
from luckyowee.models import Usuario, Foto
from flask_login import login_required, login_user, logout_user, current_user
from luckyowee.forms import FormLogin, FormCriarConta, FormFoto
import os
from werkzeug.utils import secure_filename #cria o nome_seguro para o arquivo no upload

@app.route("/", methods = ["GET", "POST"])
def homepage():
    return render_template("homepage.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    form_login = FormLogin() #crio uma instancia do FromLogin() pra usar localmente
    if form_login.validate_on_submit():
         usuario = Usuario.query.filter_by(email = form_login.email.data).first()
         if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):#compara as enha armazenada com a informada pelo usuario
            login_user(usuario)
            return redirect(url_for("profile", id_usuario = usuario.id))
    return render_template("login.html", form=form_login)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form_criarconta = FormCriarConta() #crio uma instancia do FormCriarConta() pra usar localmente
    if form_criarconta.validate_on_submit():
        senha = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data,
                          senha=senha, 
                          email=form_criarconta.email.data)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True) #loga o usuario antes de ir pro perfil
        return redirect(url_for("profile", id_usuario=usuario.id))
    return render_template("signup.html", form=form_criarconta)


@app.route("/profile/<id_usuario>", methods=["GET", "POST"])
@login_required
def profile(id_usuario):
        if int(id_usuario) == int(current_user.id):
            # usuario ve o proprio perfil
            form_foto = FormFoto()
            if form_foto.validate_on_submit():
                arquivo = form_foto.foto.data
                nome_seguro = secure_filename(arquivo.filename)
                #salvar arquivo na pasta post_pictures
                caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                                  app.config["UPLOAD_FOLDER"], 
                                  nome_seguro)
                arquivo.save(caminho)
                #registra caminho e nome do arquivo no BD
                foto = Foto(imagem=nome_seguro, id_usuario=current_user.id)
                database.session.add(foto)
                database.session.commit()
            return render_template("profile.html", usuario=current_user, form=form_foto)
        else:
             usuario = Usuario.query.get(int(id_usuario))
             return render_template("profile.html", usuario=usuario, form=None)

@app.route("/logout")
@login_required
def logout():
     logout_user() #desloga o current_user
     return redirect(url_for("homepage"))

@app.route("/feed")
@login_required
def feed():
    fotos = Foto.query.order_by(Foto.data_criacao).all() # ou se quiser limitar all()[:10]
    return render_template("feed.html", fotos=fotos)