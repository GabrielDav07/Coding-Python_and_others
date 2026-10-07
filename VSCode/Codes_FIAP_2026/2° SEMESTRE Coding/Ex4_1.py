import numpy as np                                      #pip install scikit-learn numpy
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Features: [qtd_links, tem_anexo(0/1), urgencia_no_assunto(0/1), dominio_suspeito(0/1), erros_gramaticais]
X = np.array([
    [1, 0, 0, 0, 0], [0, 0, 0, 0, 1], [2, 1, 0, 0, 0], [1, 0, 0, 0, 0],
    [8, 1, 1, 1, 5], [12, 0, 1, 1, 8], [6, 1, 1, 1, 3], [10, 1, 1, 1, 6],
    [0, 0, 0, 0, 0], [15, 1, 1, 1, 9],
])
y = np.array([0, 0, 0, 0, 1, 1, 1, 1, 0, 1])  # 0=legítimo, 1=phishing

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("--- Relatório de Classificação ---")
print(classification_report(y_test, y_pred))
print(f"Acurácia: {accuracy_score(y_test, y_pred):.2f}\n")

novo_caso = np.array([[11, 1, 1, 1, 7]])
predicao_novo = model.predict(novo_caso)[0]

classe_str = "Phishing (1)" if predicao_novo == 1 else "Legítimo (0)"
print(f"Resultado para a amostra [11, 1, 1, 1, 7]: {classe_str}")


