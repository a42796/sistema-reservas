import sqlite3

def reset_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Apaga tudo para limpar erros antigos
    cursor.execute("DROP TABLE IF EXISTS reservas")
    cursor.execute("DROP TABLE IF EXISTS recursos")
    cursor.execute("DROP TABLE IF EXISTS users")

    # Cria as tabelas da Aula 28 corretamente
    cursor.execute("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)
    """)
    cursor.execute("""
        CREATE TABLE recursos (id INTEGER PRIMARY KEY, nome TEXT, descricao TEXT)
    """)
    cursor.execute("""
        CREATE TABLE reservas (
            id INTEGER PRIMARY KEY, 
            user_id INTEGER, 
            recurso_id INTEGER, 
            data TEXT, 
            hora TEXT,
            FOREIGN KEY(recurso_id) REFERENCES recursos(id)
        )
    """)
    
    # Insere um admin e um recurso para teste
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', '123')")
    cursor.execute("INSERT INTO recursos (nome, descricao) VALUES ('Sala 1', 'Sala de Reuniões')")
    
    conn.commit()
    conn.close()
    print("Sistema limpo e pronto para a Aula 28!")

if __name__ == "__main__":
    reset_db()