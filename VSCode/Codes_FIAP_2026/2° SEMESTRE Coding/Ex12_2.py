from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV
import numpy as np

modelos = {
    "RandomForest": RandomForestClassifier(random_state=42),
    "SVM": SVC(),
    "KNN": KNeighborsClassifier(),
}

X = np.array([
    [500,80,0.1],[1200,80,0.5],[64,22,0.02],[64000,4444,10.0],[45000,8080,15.0],
    [60000,31337,20.0],[800,443,0.3],[300,53,0.05],[55000,9999,18.0],[200,25,0.2],
    [700,443,0.2],[52000,6666,17.0],[150,53,0.03],[58000,4444,19.0],[900,80,0.4],
])
y = np.array([0,0,0,1,1,1,0,0,1,0,0,1,0,1,0])

for nome, modelo in modelos.items():
    scores = cross_val_score(modelo, X, y, cv=5)
    print(f"{nome}: {scores.mean():.3f}")


grade = {"n_estimators": [100], "max_depth": [None, 5, 10]}
busca = GridSearchCV(RandomForestClassifier(random_state=42), grade, cv=5)
busca.fit(X, y)

medias = {}
for nome, modelo in modelos.items():
    scores = cross_val_score(modelo, X, y, cv=5)
    medias[nome] = scores.mean()
    print(f"{nome}: {scores.mean():.2f}")

vencedor_nome = max(medias, key=medias.get)
vencedor_modelo = modelos[vencedor_nome]
print(f"Vencedor: {vencedor_nome}")
print(f"Melhores parâmetros: {busca.best_params_}")

# Saída esperada (exemplo):
# RandomForest: 0.93
# SVM:          0.87
# KNN:          0.80
# Vencedor: RandomForest
# Melhores parâmetros: {"max_depth": None, "n_estimators": 100}