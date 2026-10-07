import mysql.connector
from mysql.connector import Error
CONFIG_DB = {
    "host": "localhost",
    "user": "root",
    "password": "senha",
    "database": "seguranca"
}
def preparar_ambiente(conexao):
    """Garante a tabela de teste populada com dados mínimos."""
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            nivel_acesso INT DEFAULT 1
        );
    """)

    cursor.execute("TRUNCATE TABLE usuarios;")
    cursor.executemany(
        "INSERT INTO usuarios (nome, email, nivel_acesso) VALUES (%s, %s, %s);",
        [
            ("Carlos Silva", "carlos@empresa.com", 3),
            ("Ana Costa", "ana@empresa.com", 5),
            ("Bruno Lima", "bruno@empresa.com", 1)
        ]
    )
    conexao.commit()
    cursor.close()
def buscar_inseguro(conexao, nome):
    """
    ❌ VULNERÁVEL: Concatenação direta de strings formatadas.
    Permite que caracteres de escape como aspas quebrem a query.
    """
    cursor = conexao.cursor(dictionary=True)
    query = f"SELECT * FROM usuarios WHERE nome = '{nome}'"
    print(f"\n[DEBUG INSEGURO] Query executada:\n  {query}")
    cursor.execute(query)
    resultados = cursor.fetchall()
    cursor.close()
    return resultados
def buscar_seguro(conexao, nome):
    """
    ✅ SEGURO: Query parametrizada.
    O placeholder %s instrui o driver a tratar o valor como dado puro.
    """
    cursor = conexao.cursor(dictionary=True)
    query = "SELECT * FROM usuarios WHERE nome = %s"
    cursor.execute(query, (nome,))
    resultados = cursor.fetchall()
    cursor.close()
    return resultados
def executar_poc():
    try:
        conexao = mysql.connector.connect(**CONFIG_DB)
        preparar_ambiente(conexao)
        entrada_maliciosa = "' OR '1'='1"
        print("=" * 60)
        print(" TESTE DE SQL INJECTION: CONCATENADO vs PARAMETRIZADO")
        print("=" * 60)
        print(f"Payload de teste: {entrada_maliciosa}")
        # 1. Teste da função insegura
        res_inseguro = buscar_inseguro(conexao, entrada_maliciosa)
        print(f"[INSEGURO] entrada: {entrada_maliciosa} -> {len(res_inseguro)} usuários retornados (VAZAMENTO!)")
        for u in res_inseguro:
            print(f"   -> ID: {u['id']} | Nome: {u['nome']} | Email: {u['email']} | Nível: {u['nivel_acesso']}")

        res_seguro = buscar_seguro(conexao, entrada_maliciosa)
        print(f"\n[SEGURO]   entrada: {entrada_maliciosa} -> {len(res_seguro)} usuários retornados (defesa OK)")
        print("\n" + "=" * 60)
        print("CONCLUSÃO TÉCNICA:")
        print("A query parametrizada isola o dado do comando executável.")
        print("O banco procurou literalmente pelo nome \"' OR '1'='1\" em vez de")
        print("executar a expressão lógica OR TRUE. Vulnerabilidade mitigada!")
        print("=" * 60)
        conexao.close()
    except Error as e:
        print(f"[-] Erro MySQL: {e}")
if __name__ == "__main__":
    executar_poc()