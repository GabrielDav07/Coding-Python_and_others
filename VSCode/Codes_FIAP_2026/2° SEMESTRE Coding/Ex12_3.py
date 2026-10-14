
import hashlib
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

modelos = {
    "RandomForest": RandomForestClassifier(random_state=42),
    "SVM": SVC(),
    "KNN": KNeighborsClassifier(),
}

X = np.array([
    [500,80,0.1], [1200,80,0.5], [64,22,0.02],
    [64000,4444,10.0], [45000,8080,15.0],
    [60000,31337,20.0], [800,443,0.3],
    [300,53,0.05], [55000,9999,18.0], [200,25,0.2],
    [700,443,0.2], [52000,6666,17.0],
    [150,53,0.03], [58000,4444,19.0], [900,80,0.4],
])

y = np.array([0,0,0,1,1,1,0,0,1,0,0,1,0,1,0])

medias = {}

for nome, modelo in modelos.items():
    scores = cross_val_score(modelo, X, y, cv=5)
    medias[nome] = scores.mean()
    print(f"{nome}: {scores.mean():.3f}")

vencedor_nome = max(medias, key=medias.get)
print(f"Vencedor: {vencedor_nome}")

grade = {
    "n_estimators": [100],
    "max_depth": [None, 5, 10],
}

busca = GridSearchCV(
    RandomForestClassifier(random_state=42),
    grade,
    cv=5
)
busca.fit(X, y)

print(f"Melhores parâmetros do Random Forest: {busca.best_params_}")

if vencedor_nome == "RandomForest":
    melhor_modelo = busca.best_estimator_
else:
    melhor_modelo = modelos[vencedor_nome].fit(X, y)

nome_arquivo = "modelo_seguranca.pkl"
joblib.dump(melhor_modelo, nome_arquivo)

print(f"\nModelo salvo: {nome_arquivo}")

def calcular_hash(caminho):
    sha256 = hashlib.sha256()

    with open(caminho, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(4096), b""):
            sha256.update(bloco)

    return sha256.hexdigest()

hash_original = calcular_hash(nome_arquivo)
print(f"Hash SHA-256: {hash_original}")

print("Recarregando e verificando integridade...")

hash_atual = calcular_hash(nome_arquivo)

if hash_original == hash_atual:
    modelo = joblib.load(nome_arquivo)

    previsao = modelo.predict([[700, 443, 0.2]])
    print(f"Hash confere: modelo íntegro. Previsão de teste: {previsao}")
else:
    print("ALERTA: arquivo do modelo foi modificado!")
