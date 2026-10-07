import numpy as np
from sklearn.ensemble import IsolationForest
# Features: [hora_do_dia, tentativas_login, bytes_baixados]
acessos = np.array([
    [9, 1, 200],       # Amostra 0: Normal
    [10, 1, 500],      # Amostra 1: Normal
    [14, 2, 300],      # Amostra 2: Normal
    [11, 1, 250],      # Amostra 3: Normal
    [16, 1, 400],      # Amostra 4: Normal
    [3, 40, 900000],   # Amostra 5: ANÔMALO (3h madrugada, 40 tentativas, 900 KB)
    [10, 1, 350],      # Amostra 6: Normal
    [15, 2, 280],      # Amostra 7: Normal
    [2, 55, 800000],   # Amostra 8: ANÔMALO (2h madrugada, 55 tentativas, 800 KB)
])
def detectar_anomalias():
    # contamination=0.25 pois temos 2 anomalias evidentes em 9 amostras (~22%)
    detector = IsolationForest(contamination=0.25, random_state=42)
    detector.fit(acessos)

    resultados = detector.predict(acessos)
    print("==================================================")
    print("     DETECÇÃO DE ACESSOS ANÔMALOS (ISOLATION FOREST)")
    print("==================================================")
    for i, (amostra, pred) in enumerate(zip(acessos, resultados)):
        status = "ANOMALIA" if pred == -1 else "Normal"
        alerta = " ⚠️ [ALERTA DE SOC]" if pred == -1 else ""
        print(f"Amostra {i}: {amostra.tolist()} -> {status}{alerta}")
    print("\nResumo da Análise:")
    print("As amostras 5 e 8 foram isoladas com poucos cortes pelo algoritmo,")
    print("pois combinam horário fora de expediente (2h-3h), alto volume de requisições")
    print("e consumo de banda desproporcional, sugerindo exfiltração ou força bruta.")
if __name__ == "__main__":
    detectar_anomalias()