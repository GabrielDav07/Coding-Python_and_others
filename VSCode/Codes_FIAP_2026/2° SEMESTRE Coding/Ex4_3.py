from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score, accuracy_score

y_verdadeiro = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1]
y_previsto   = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
def avaliar_metricas():
    # Matriz de confusão: [[TN, FP], [FN, TP]]
    matriz = confusion_matrix(y_verdadeiro, y_previsto)
    precisao = precision_score(y_verdadeiro, y_previsto)
    recall = recall_score(y_verdadeiro, y_previsto)
    f1 = f1_score(y_verdadeiro, y_previsto)
    acuracia = accuracy_score(y_verdadeiro, y_previsto)
    print("==================================================")
    print("      AVALIAÇÃO DE MÉTRICAS EM DADOS DESBALANCEADOS")
    print("==================================================")
    print(f"Matriz de Confusão:\n{matriz}\n")
    print(f"Acurácia:  {acuracia:.2f} (90%)")
    print(f"Precisão:  {precisao:.2f} (100%)")
    print(f"Recall:    {recall:.2f} (50%)")
    print(f"F1-Score:  {f1:.2f}")
    print("\n" + "=" * 50)
    print("JUSTIFICATIVA TÉCNICA (3 LINHAS CONFORME ENUNCIADO):")
    print("1. Uma acurácia de 90% gera uma falsa sensação de segurança causada pelo desbalanceamento de classes.")
    print("2. O recall de apenas 0.50 (50%) revela que metade dos ataques reais passou completamente despercebida.")
    print("3. Em cibersegurança, o recall é prioritário pois o custo de um falso negativo (brecha não detectada) é crítico.")
    print("=" * 50)
if __name__ == "__main__":
    avaliar_metricas()