import sqlite3

def query(sql, params=(), fetchone=False, fetchall=False):
    with sqlite3.connect("empresa.db") as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            if fetchone: return cursor.fetchone()
            if fetchall: return cursor.fetchall()
            return cursor.rowcount
        except sqlite3.IntegrityError:
            return "ERRO_DUPLICADO"

query("""CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, email TEXT UNIQUE, nivel_acesso INTEGER CHECK(nivel_acesso BETWEEN 1 AND 5)
)""")

if query("SELECT COUNT(*) FROM usuarios", fetchone=True)[0] == 0:
    for u in [("Carlos Silva", "carlos@empresa.com", 3), ("Ana Costa", "ana@empresa.com", 5), ("Bruno Lima", "bruno@empresa.com", 1)]:
        query("INSERT INTO usuarios (nome, email, nivel_acesso) VALUES (?, ?, ?)", u)

def cadastrar():
    nome, email = input("Nome: "), input("E-mail: ")
    try:
        nivel = int(input("Nível (1-5): "))
        if not 1 <= nivel <= 5: return print("Erro: Nível deve ser entre 1 e 5.")
    except ValueError: return print("Erro: Digite um número.")
    res = query("INSERT INTO usuarios (nome, email, nivel_acesso) VALUES (?, ?, ?)", (nome, email, nivel))
    print("Erro: email já existe" if res == "ERRO_DUPLICADO" else "Ativo cadastrado!")

def listar():
    for u in query("SELECT nome, email, nivel_acesso FROM usuarios", fetchall=True):
        print(f"{u[0]:<12} | {u[1]:<20} | nível {u[2]}")

def buscar():
    u = query("SELECT nome, email, nivel_acesso FROM usuarios WHERE email = ?", (input("E-mail: "),), fetchone=True)
    print(f"{u[0]} | {u[1]} | nível {u[2]}" if u else "Usuário não encontrado.")

def alterar():
    email = input("E-mail: ")
    try:
        nivel = int(input("Novo nível (1-5): "))
        if not 1 <= nivel <= 5: return print("Erro: Nível deve ser entre 1 e 5.")
    except ValueError: return print("Erro: Digite um número.")
    res = query("UPDATE usuarios SET nivel_acesso = ? WHERE email = ?", (nivel, email))
    print("Nível atualizado!" if res else "Usuário não encontrado.")

def remover():
    res = query("DELETE FROM usuarios WHERE email = ?", (input("E-mail: "),))
    print("Usuário removido!" if res else "Usuário não encontrado.")

acoes = {"1": cadastrar, "2": listar, "3": buscar, "4": alterar, "5": remover}
while True:
    print("\n[1] Cadastrar | [2] Listar | [3] Buscar | [4] Promover/Rebaixar | [5] Remover | [6] Sair")
    op = input("Opção: ")
    if op == "6": break
    acoes.get(op, lambda: print("Opção inválida!"))()