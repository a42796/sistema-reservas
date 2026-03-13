import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, flash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = "tech_core_secure_key_2024"

# --- CONEXÃO BD ---
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  
    return conn

# --- PROTEÇÃO DE ROTAS ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# --- ROTAS BASE ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/contactos")
def contactos():
    return render_template("form.html")

@app.route("/enviar", methods=["POST"])
def enviar():
    nome = request.form.get("nome")
    email = request.form.get("email")
    mensagem = request.form.get("mensagem")
    return render_template("resultado.html", nome=nome, email=email, mensagem=mensagem)

# --- AUTENTICAÇÃO ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")
        
        db = get_db()
        usuario = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (user, pw)).fetchone()
        db.close()

        if usuario:
            session["user"] = usuario["username"]
            session["user_id"] = usuario["id"]
            flash(f"Bem-vindo, {user}!", "success")
            return redirect(url_for("dashboard"))
        
        flash("Credenciais Inválidas!", "danger")
    return render_template("login.html")

@app.route("/registo", methods=["GET", "POST"])
def registo():
    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pw))
            db.commit()
            db.close()
            return render_template("sucesso_registo.html", nome=user)
        except:
            flash("Erro: Este utilizador já existe!", "danger")
            return redirect(url_for("registo"))
    return render_template("registo.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sessão terminada.", "info")
    return redirect(url_for("index"))

# --- PERFIL E DASHBOARD ---
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", nome=session["user"])

@app.route("/perfil")
@login_required
def perfil():
    return render_template("perfil.html", nome=session["user"])

# --- GESTÃO DE UTILIZADORES (ADMIN) ---
@app.route("/users")
@login_required
def listar_utilizadores():
    db = get_db()
    users = db.execute("SELECT id, username FROM users").fetchall()
    db.close()
    return render_template("users.html", users=users)

@app.route("/users/delete/<int:id>")
@login_required
def delete_user(id):
    db = get_db()
    db.execute("DELETE FROM users WHERE id = ?", (id,))
    db.commit()
    db.close()
    flash("Utilizador removido!", "warning")
    return redirect(url_for("listar_utilizadores"))

# --- GESTÃO DE RESERVAS ---

# 1. LISTAGEM (A que dava erro de BuildError)
@app.route("/reservas")
@login_required
def listar_reservas():
    db = get_db()
    user_id = session.get("user_id")
    f_recurso = request.args.get("recurso_id")
    f_data = request.args.get("data")
    
    query = "SELECT r.*, rec.nome AS nome_recurso FROM reservas r JOIN recursos rec ON r.recurso_id = rec.id WHERE r.user_id = ?"
    params = [user_id]
    
    if f_recurso:
        query += " AND r.recurso_id = ?"
        params.append(f_recurso)
    if f_data:
        query += " AND r.data = ?"
        params.append(f_data)
        
    reservas = db.execute(query, params).fetchall()
    recursos = db.execute("SELECT * FROM recursos").fetchall()
    db.close()
    return render_template("reservas.html", reservas=reservas, recursos=recursos, f_recurso=f_recurso, f_data=f_data)

# 2. NOVA RESERVA (A função que o Flask não encontrava!)
@app.route("/reservas/nova")
@login_required
def criar_reserva():
    db = get_db()
    recursos = db.execute("SELECT * FROM recursos").fetchall()
    db.close()
    return render_template("criar_reserva.html", recursos=recursos)

@app.route("/reservas/delete/<int:id>")
@login_required
def delete_reserva(id):
    db = get_db()
    db.execute("DELETE FROM reservas WHERE id = ?", (id,))
    db.commit()
    db.close()
    return redirect(url_for("listar_reservas"))

@app.route("/reservas/editar/<int:id>")
@login_required
def editar_reserva(id):
    # Rota vazia apenas para não dar erro no botão de editar
    flash("Edição disponível em breve!", "info")
    return redirect(url_for("listar_reservas"))

# --- RELATÓRIOS ---
@app.route("/relatorios")
@login_required
def menu_relatorios():
    db = get_db()
    resumo = db.execute("""
        SELECT recursos.id, recursos.nome, COUNT(reservas.id) as total 
        FROM recursos 
        LEFT JOIN reservas ON recursos.id = reservas.recurso_id 
        GROUP BY recursos.id
    """).fetchall()
    db.close()
    # Verifica se o ficheiro na pasta templates se chama exatamente assim:
    return render_template("menu_relatorios.html", resumo=resumo)

@app.route("/relatorio/recurso/<int:recurso_id>")
@login_required
def relatorio_por_recurso(recurso_id):
    db = get_db()
    reservas = db.execute("""
        SELECT r.*, u.username, rec.nome as nome_recurso
        FROM reservas r
        JOIN users u ON r.user_id = u.id
        JOIN recursos rec ON r.recurso_id = rec.id
        WHERE r.recurso_id = ?
    """, (recurso_id,)).fetchall()
    
    recurso = db.execute("SELECT nome FROM recursos WHERE id = ?", (recurso_id,)).fetchone()
    db.close()
    return render_template("relatorio_detalhado.html", 
                           reservas=reservas, 
                           titulo=recurso['nome'] if recurso else "Relatório",
                           now=datetime.now())

if __name__ == "__main__":
    app.run(debug=True)