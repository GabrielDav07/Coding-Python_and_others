from pymongo import MongoClient
from datetime import datetime
def conectar_eventos():
    client = MongoClient("mongodb://localhost:27017/")
    return client["seguranca"]["eventos_auth"]
def consultar(fonte=None, tipo=None, ip=None, desde=None):
    """
    Monta dinamicamente a query com base apenas nos argumentos fornecidos.
    
    :param fonte: Nome da fonte (ex: 'auth', 'firewall')
    :param tipo: Tipo do evento (ex: 'FAIL', 'OK')
    :param ip: Endereço IP de origem
    :param desde: Objeto datetime para início da janela temporal ($gte)
    :return: Lista de documentos ordenados por timestamp decrescente
    """
    colecao = conectar_eventos()
    filtro = {}
    if fonte is not None:
        filtro["fonte"] = fonte
    if tipo is not None:
        filtro["tipo"] = tipo
    if ip is not None:
        filtro["ip"] = ip
    if desde is not None:
        filtro["timestamp"] = {"$gte": desde}

    cursor = colecao.find(filtro, {"_id": 0}).sort("timestamp", -1)
    return list(cursor)
def demonstrar_consultas():
    print("--- Teste 1: Filtrar apenas FAIL do IP 185.220.101.1 ---")
    resultados_1 = consultar(tipo="FAIL", ip="185.220.101.1")
    print(f"Total encontrado: {len(resultados_1)}")
    for r in resultados_1[:3]:  # exibe os 3 primeiros
        print(f"  {r['timestamp']} | {r['tipo']} | {r['ip']} | usuario={r.get('usuario')}")
    print("\n--- Teste 2: Filtrar todos os eventos da fonte 'auth' ---")
    resultados_2 = consultar(fonte="auth")
    print(f"Total encontrado: {len(resultados_2)}")
    print("\n--- Teste 3: Eventos a partir de 08:15:30 ---")
    data_corte = datetime(2025, 2, 20, 8, 15, 30)
    resultados_3 = consultar(desde=data_corte)
    print(f"Total encontrado: {len(resultados_3)}")
    for r in resultados_3:
        print(f"  {r['timestamp']} | {r['tipo']} | {r['ip']}")
if __name__ == "__main__":
    demonstrar_consultas()