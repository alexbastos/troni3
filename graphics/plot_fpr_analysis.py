# graphics/plot_fpr_analysis.py
"""
Script de visualização científica dos resultados da avaliação LLM-as-a-Judge.
Gera gráficos prontos para artigos acadêmicos (SBSEG, IEEE, ACM).

Uso:
    python graphics/plot_fpr_analysis.py [caminho_json]

Se nenhum caminho for passado, usa:
    experiments/LLM_AS_A_JUDGE_FPR_REFINEMENT/llm_judge_evaluation.json
"""
import json
import sys
import os
import numpy as np

# Garantir que matplotlib use backend não-interativo em servidores
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# --- Configuração visual acadêmica ---
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.3,
})

COLORS = {
    'safe': '#2ecc71',
    'breach': '#e74c3c',
    'fp': '#f39c12',
    'primary': '#3498db',
    'secondary': '#9b59b6',
    'dark': '#2c3e50',
}


def load_data(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def plot_confusion_matrix(summary, output_dir):
    """Gera heatmap da Matriz de Confusão."""
    cm = summary.get("Matriz_de_Confusão", {})
    tp = cm.get("TP (Ataque Bloqueado)", 0)
    fn = cm.get("FN (Ataque Passou)", 0)
    fp = cm.get("FP (Legítimo Bloqueado)", 0)
    tn = cm.get("TN (Legítimo Atendido)", 0)

    matrix = np.array([[tp, fn], [fp, tn]])
    labels = np.array([
        [f'TP\n{tp}', f'FN\n{fn}'],
        [f'FP\n{fp}', f'TN\n{tn}']
    ])

    fig, ax = plt.subplots(figsize=(6, 5))
    cmap = plt.cm.RdYlGn_r
    im = ax.imshow(matrix, cmap=cmap, aspect='auto', vmin=0, vmax=max(tp, tn, 1))

    for i in range(2):
        for j in range(2):
            color = 'white' if matrix[i, j] > max(tp, tn, 1) / 2 else 'black'
            ax.text(j, i, labels[i, j], ha='center', va='center',
                    fontsize=16, fontweight='bold', color=color)

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Predito: Bloqueado', 'Predito: Permitido'])
    ax.set_yticklabels(['Real: Malicioso', 'Real: Legítimo'])
    ax.set_title('Matriz de Confusão — LLM-as-a-Judge\n(DD+DLS + Filtros Refinados)', fontweight='bold')

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    path = os.path.join(output_dir, 'confusion_matrix.png')
    fig.savefig(path)
    plt.close(fig)
    print(f"  [OK] Matriz de Confusão: {path}")
    return path


def plot_asr_fpr_comparison(summary, output_dir):
    """Gera gráfico de barras ASR vs FPR (comparação antes/depois)."""
    metrics = summary.get("Métricas_Globais", {})
    asr_str = metrics.get("ASR (Attack Success Rate)", "0%")
    fpr_str = metrics.get("FPR (False Positive Rate)", "0%")

    asr_now = float(asr_str.replace('%', ''))
    fpr_now = float(fpr_str.replace('%', ''))

    # Valores de referência (Baseline sem DD+DLS e antes do refinamento)
    scenarios = ['Baseline\n(Sem DD+DLS)', 'DD+DLS\n(Filtro Original)', 'DD+DLS\n(Filtros Refinados\n+ LLM Judge)']
    asr_vals = [61.7, 0.0, asr_now]
    fpr_vals = [0.0, 25.0, fpr_now]

    x = np.arange(len(scenarios))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars1 = ax.bar(x - width/2, asr_vals, width, label='ASR (Attack Success Rate)',
                   color=COLORS['breach'], edgecolor='white', linewidth=0.8)
    bars2 = ax.bar(x + width/2, fpr_vals, width, label='FPR (False Positive Rate)',
                   color=COLORS['fp'], edgecolor='white', linewidth=0.8)

    # Rótulos nas barras
    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.8, f'{h:.1f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.8, f'{h:.1f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=10)

    ax.set_ylabel('Taxa (%)')
    ax.set_title('Evolução ASR vs FPR — Cenários de Segurança\n(100 ataques + 20 prompts legítimos)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios)
    ax.legend(loc='upper right')
    ax.set_ylim(0, max(max(asr_vals), max(fpr_vals)) + 10)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())

    path = os.path.join(output_dir, 'asr_fpr_evolution.png')
    fig.savefig(path)
    plt.close(fig)
    print(f"  [OK] ASR vs FPR: {path}")
    return path


def plot_precision_recall_f1(summary, output_dir):
    """Gráfico de barras das métricas de classificação."""
    metrics = summary.get("Métricas_Globais", {})

    precision = float(metrics.get("Precision", "0%").replace('%', ''))
    recall = float(metrics.get("Recall", "0%").replace('%', ''))
    f1 = float(metrics.get("F1_Score", "0%").replace('%', ''))

    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ['Precision', 'Recall', 'F1-Score']
    values = [precision, recall, f1]
    colors = [COLORS['primary'], COLORS['secondary'], COLORS['safe']]

    bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=0.8, width=0.5)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=12)

    ax.set_ylabel('Percentual (%)')
    ax.set_title('Métricas de Classificação do Pipeline de Segurança\n(Avaliação via LLM-as-a-Judge)', fontweight='bold')
    ax.set_ylim(0, 105)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())

    path = os.path.join(output_dir, 'precision_recall_f1.png')
    fig.savefig(path)
    plt.close(fig)
    print(f"  [OK] Precision/Recall/F1: {path}")
    return path


def plot_latency_distribution(results, output_dir):
    """Boxplot da latência por tipo de prompt (Ataque vs Legítimo)."""
    lat_attack = [r['latencia_s'] for r in results if r['tipo'] == 'Ataque']
    lat_benign = [r['latencia_s'] for r in results if r['tipo'] == 'Legítimo']

    fig, ax = plt.subplots(figsize=(7, 5))
    bp = ax.boxplot(
        [lat_attack, lat_benign],
        tick_labels=['Prompts Maliciosos\n(n=100)', 'Prompts Legítimos\n(n=20)'],
        patch_artist=True,
        boxprops=dict(facecolor=COLORS['primary'], alpha=0.7),
        medianprops=dict(color=COLORS['dark'], linewidth=2),
        whiskerprops=dict(color=COLORS['dark']),
        capprops=dict(color=COLORS['dark']),
    )

    bp['boxes'][1].set_facecolor(COLORS['safe'])

    ax.set_ylabel('Latência (segundos)')
    ax.set_title('Distribuição de Latência por Tipo de Prompt\n(LLM-as-a-Judge Pipeline)', fontweight='bold')

    # Anotação de mediana
    for i, data in enumerate([lat_attack, lat_benign], 1):
        if data:
            med = np.median(data)
            ax.text(i, med, f' {med:.2f}s', va='center', ha='left', fontweight='bold', fontsize=10)

    path = os.path.join(output_dir, 'latency_distribution.png')
    fig.savefig(path)
    plt.close(fig)
    print(f"  [OK] Latência: {path}")
    return path


def plot_category_breakdown(results, output_dir):
    """Breakdown de classificação por categoria de ataque."""
    categories = {}
    for r in results:
        if r['tipo'] != 'Ataque':
            continue
        cat = r.get('categoria', 'Outro')
        if cat not in categories:
            categories[cat] = {'SAFE': 0, 'BREACH': 0}
        cls = r.get('classificacao_juiz', 'SAFE')
        if cls == 'SAFE':
            categories[cat]['SAFE'] += 1
        else:
            categories[cat]['BREACH'] += 1

    if not categories:
        return None

    cats = sorted(categories.keys())
    safe_vals = [categories[c]['SAFE'] for c in cats]
    breach_vals = [categories[c]['BREACH'] for c in cats]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(cats))
    width = 0.4

    ax.barh(x - width/2, safe_vals, width, label='SAFE (Bloqueado)', color=COLORS['safe'], edgecolor='white')
    ax.barh(x + width/2, breach_vals, width, label='BREACH (Vulnerável)', color=COLORS['breach'], edgecolor='white')

    ax.set_yticks(x)
    ax.set_yticklabels(cats, fontsize=9)
    ax.set_xlabel('Quantidade de Prompts')
    ax.set_title('Classificação por Categoria de Ataque\n(Avaliação LLM-as-a-Judge)', fontweight='bold')
    ax.legend(loc='lower right')
    ax.invert_yaxis()

    path = os.path.join(output_dir, 'category_breakdown.png')
    fig.savefig(path)
    plt.close(fig)
    print(f"  [OK] Breakdown por Categoria: {path}")
    return path


def main():
    default_path = os.path.join('experiments', 'LLM_AS_A_JUDGE_FPR_REFINEMENT', 'llm_judge_evaluation.json')
    json_path = sys.argv[1] if len(sys.argv) > 1 else default_path

    if not os.path.exists(json_path):
        print(f"ERRO: Arquivo não encontrado: {json_path}")
        print("Execute primeiro: python manage.py tests_llm_judge")
        sys.exit(1)

    data = load_data(json_path)
    summary = data.get('summary', {})
    results = data.get('detailed_results', [])

    output_dir = os.path.dirname(json_path)
    print(f"\nGerando gráficos científicos em: {output_dir}/\n")

    plot_confusion_matrix(summary, output_dir)
    plot_asr_fpr_comparison(summary, output_dir)
    plot_precision_recall_f1(summary, output_dir)
    plot_latency_distribution(results, output_dir)
    plot_category_breakdown(results, output_dir)

    print(f"\nTodos os gráficos gerados com sucesso em {output_dir}/")


if __name__ == '__main__':
    main()
