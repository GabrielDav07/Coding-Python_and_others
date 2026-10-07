import mysql.connector
from mysql.connector import Error
CONFIG_DB = {
    "host": "localhost",
    "user": "root",
    "password": "senha",
    "database": "seguranca"
}
def preparar_tabela_alertas(conexao):
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tipo VARCHAR(50) NOT NULL,
            ip_origem VARCHAR(45) NOT NULL,
            severidade ENUM('baixa', 'media', 'alta', 'critica') NOT NULL,
            status VARCHAR(20) DEFAULT 'aberto',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("TRUNCATE TABLE alertas;")
    registros = [
        ("BRUTE_FORCE", "185.220.101.1", "critica", "aberto"),
        ("BRUTE_FORCE", "185.220.101.1", "critica", "aberto"),
        ("BRUTE_FORCE", "185.220.101.1", "critica", "aberto"),
        ("BRUTE_FORCE", "185.220.101.1", "alta",    "aberto"),
        ("PORT_SCAN",   "45.33.32.156",  "alta",    "aberto"),
        ("PORT_SCAN",   "45.33.32.156",  "alta",    "aberto"),
        ("PORT_SCAN",   "45.33.32.156",  "media",   "aberto"),
        ("XSS",         "91.240.118.172","alta",    "aberto"),
        ("XSS",         "192.168.1.80",  "media",   "resolvido"),
        ("SQLI",        "91.240.118.172","baixa",   "aberto"),
    ]
    cursor.executemany(
        "INSERT INTO alertas (tipo, ip_origem, severidade, status) VALUES (%s, %s, %s, %s)",
        registros
    )
    conexao.commit()
    cursor.close()
def gerar_relatorio():
    try:
        conexao = mysql.connector.connect(**CONFIG_DB)
        preparar_tabela_alertas(conexao)
        cursor = conexao.cursor(dictionary=True)
        print("==================================================")
        print("          RELATÓRIO DE ALERTAS DO SOC             ")
        print("==================================================")

        cursor.execute("""
            SELECT severidade, COUNT(*) AS total
            FROM alertas
            GROUP BY severidade
            ORDER BY FIELD(severidade, 'critica', 'alta', 'media', 'baixa');
        """)
        linhas_sev = cursor.fetchall()
        partes_sev = [f"{r['severidade']}: {r['total']}" for r in linhas_sev]
        print(f"=== Por severidade ===  {' | '.join(partes_sev)}")
        cursor.execute("""
            SELECT tipo, COUNT(*) AS total
            FROM alertas
            GROUP BY tipo
            ORDER BY total DESC;
        """)
        linhas_tipo = cursor.fetchall()
        partes_tipo = [f"{r['tipo']}: {r['total']}" for r in linhas_tipo]
        print(f"=== Por tipo ===        {' | '.join(partes_tipo)}")
        cursor.execute("""
            SELECT ip_origem, COUNT(*) AS total
            FROM alertas
            GROUP BY ip_origem
            ORDER BY total DESC
            LIMIT 5;
        """)
        print("\n=== Top IPs de origem ===")
        for r in cursor.fetchall():
            print(f"{r['ip_origem']:<15} -> {r['total']} alertas")
        print("==================================================")
        cursor.close()
        conexao.close()
    except Error as e:
        print(f"[-] Erro ao emitir relatório: {e}")
if __name__ == "__main__":
    gerar_relatorio()