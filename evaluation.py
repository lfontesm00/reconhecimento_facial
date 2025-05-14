import csv
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def run_tests(scenarios, model, preprocess_fn, csv_path="resultados.csv"):
    """
    Executa testes em múltiplos cenários, mede métricas e salva resultados em um CSV.
    scenarios: lista de dicionários com chaves 'images', 'labels', 'nome'.
    model: instância do modelo com método predict().
    preprocess_fn: função para pré-processar as imagens.
    csv_path: caminho do arquivo CSV de saída.
    """
    resultados = []
    for scenario in scenarios:
        images = scenario['images']
        labels = scenario['labels']
        nome = scenario.get('nome', 'cenário')
        y_true = []
        y_pred = []
        for img, label in zip(images, labels):
            img_proc = preprocess_fn(img)
            pred, _ = model.predict(img_proc)
            y_true.append(label)
            y_pred.append(pred)
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        resultados.append({
            'cenario': nome,
            'acuracia': acc,
            'precisao': prec,
            'revocacao': rec,
            'f1': f1
        })
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['cenario', 'acuracia', 'precisao', 'revocacao', 'f1'])
        writer.writeheader()
        for row in resultados:
            writer.writerow(row)
    return resultados 