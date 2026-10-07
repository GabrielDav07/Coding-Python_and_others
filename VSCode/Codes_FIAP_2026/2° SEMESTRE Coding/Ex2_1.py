import mongomock                 #pip install mongomock
from pymongo import errors


client = mongomock.MongoClient()
db = client["inventario_db"]
colecao = db["ativos"]

colecao.create_index("ip", unique=True)

ativos_iniciais = [
    {"nome": "SRV-WEB01", "tipo": "servidor", "ip": "192.168.1.10", "status": "ativo"},
    {"nome": "PC-RH03", "tipo": "estacao", "ip": "192.168.1.45", "status": "ativo"},
    {"nome": "SW-CORE01", "tipo": "switch", "ip": "192.168.1.1", "status": "inativo"},
]

if colecao.count_documents({}) == 0:
    colecao.insert_many(ativos_iniciais)

def cadastrar():
    print("\n--- [1] Cadastrar Ativo ---")
    nome = input("Nome: ")
    tipo = input("Tipo: ")
    ip = input("IP: ")
    status = input("Status: ")
    try:
        colecao.insert_one({"nome": nome, "tipo": tipo, "ip": ip, "status": status})
        print("Ativo cadastrado!")
    except errors.DuplicateKeyError:
        print("Erro: IP já cadastrado!")

def listar():
    print("\n--- [2] Listar Ativos ---")
    ativos = list(colecao.find({}, {"_id": 0}))
    if not ativos:
        print("Nenhum ativo encontrado.")
        return
    
    print(f"{'NOME':<12} | {'TIPO':<10} | {'IP':<15} | {'STATUS':<10}")
    print("-" * 55)
    for a in ativos:
        print(f"{a.get('nome',''):<12} | {a.get('tipo',''):<10} | {a.get('ip',''):<15} | {a.get('status',''):<10}")

def buscar_por_ip():
    print("\n--- [3] Buscar por IP ---")
    ip = input("Digite o IP: ")
    ativo = colecao.find_one({"ip": ip}, {"_id": 0})
    if ativo:
        print(f"Encontrado: {ativo}")
    else:
        print("Ativo não encontrado!")

def atualizar_status():
    print("\n--- [4] Atualizar Status ---")
    ip = input("Digite o IP do ativo: ")
    novo_status = input("Novo Status: ")
    resultado = colecao.update_one({"ip": ip}, {"$set": {"status": novo_status}})
    if resultado.matched_count > 0:
        print("Status atualizado!")
    else:
        print("Ativo não encontrado!")

def remover():
    print("\n--- [5] Remover Ativo ---")
    ip = input("Digite o IP do ativo a remover: ")
    resultado = colecao.delete_one({"ip": ip})
    if resultado.deleted_count > 0:
        print("Ativo removido!")
    else:
        print("Ativo não encontrado!")

def menu():
    while True:
        print("\n=== MENU INVENTÁRIO DE ATIVOS ===")
        print("[1] Cadastrar")
        print("[2] Listar")
        print("[3] Buscar por IP")
        print("[4] Atualizar status")
        print("[5] Remover")
        print("[6] Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar()
        elif opcao == "2":
            listar()
        elif opcao == "3":
            buscar_por_ip()
        elif opcao == "4":
            atualizar_status()
        elif opcao == "5":
            remover()
        elif opcao == "6":
            print("Saindo...")
            break
        else:
            print("Opção inválida!")


if __name__ == "__main__":
    menu()