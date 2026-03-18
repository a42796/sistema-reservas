import sqlite3

def criar_base_de_dados():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recursos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recurso_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (recurso_id) REFERENCES recursos (id)
        )
    ''')


    recursos_iniciais = [
        ('Sala de Reuniões A', 'Sala'),
        ('Auditório Principal', 'Espaço'),
        ('Portátil Dell XP', 'Equipamento'),
        ('Projetor HD', 'Equipamento')
    ]
    
    cursor.executemany('INSERT INTO recursos (nome, tipo) VALUES (?, ?)', recursos_iniciais)

    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', '123'))
    except sqlite3.IntegrityError:
        pass 

    conn.commit()
    conn.close()
    print("Base de dados 'database.db' criada com sucesso!")

if __name__ == "__main__":
    criar_base_de_dados()