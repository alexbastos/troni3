import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    # Caminho do arquivo
    json_path = "scientific_evaluation.json"
    output_dir = "experiments/DD_DLS"

    if not os.path.exists(json_path):
        print(f"Arquivo {json_path} não encontrado!")
        return

    # Cria diretório de experimentos
    os.makedirs(output_dir, exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Copiar o json para a pasta do experimento (backup)
    with open(os.path.join(output_dir, "scientific_evaluation_backup.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Extrai ASR Geral
    asr_puro = data["ASR_Geral"]["LLM_Puro"]
    asr_rag = data["ASR_Geral"]["LLM_RAG"]

    # 1. Gráfico de Barras: ASR Comparativo
    plt.figure(figsize=(8, 6))
    bars = plt.bar(["LLM Puro (Direto)", "LLM + RAG (Indireto)"], [asr_puro, asr_rag], color=['#4CAF50', '#2196F3'])
    plt.ylim(0, 100)
    plt.title("Attack Success Rate (ASR) - Cenário DD_DLS\n(Delimitadores Dinâmicos + Dual-LLM)", fontsize=14, fontweight='bold')
    plt.ylabel("ASR (%)", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Adiciona rótulos numéricos
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1.5, f"{yval:.1f}%", ha='center', va='bottom', fontweight='bold', fontsize=12)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "asr_comparativo.png"), dpi=300)
    plt.close()

    # 2. Breakdown por Categoria (RAG)
    categorias = data["Stats"]["Categorias_RAG"]
    nomes_cat = list(categorias.keys())
    vulns = [categorias[c]["vulneravel_fn"] for c in nomes_cat]
    protegidos = [categorias[c]["protegido_tp"] for c in nomes_cat]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(nomes_cat))
    width = 0.35

    ax.bar(x, protegidos, width, label='Protegido (Falha Segura)', color='#4CAF50')
    ax.bar([i + width for i in x], vulns, width, label='Vulnerável (Ataque Bem Sucedido)', color='#F44336')

    ax.set_ylabel('Quantidade de Prompts')
    ax.set_title('Eficácia da Segurança por Categoria de Ataque (Camada RAG)', fontsize=14, fontweight='bold')
    ax.set_xticks([i + width / 2 for i in x])
    ax.set_xticklabels(nomes_cat, rotation=15, ha="right")
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "categoria_breakdown.png"), dpi=300)
    plt.close()

    # 3. Latência (Overhead Comparativo)
    lat_puro = []
    lat_rag = []
    for d in data["Raw_Data"]:
        if d["LLM_Puro"]["latencia_s"] > 0:
            lat_puro.append(d["LLM_Puro"]["latencia_s"])
        if d["LLM_RAG"]["latencia_s"] > 0:
            lat_rag.append(d["LLM_RAG"]["latencia_s"])

    plt.figure(figsize=(8, 6))
    sns.boxplot(data=[lat_puro, lat_rag], palette=["#4CAF50", "#2196F3"])
    plt.xticks([0, 1], ["LLM Puro", "LLM + RAG"])
    plt.ylabel("Tempo de Resposta (segundos)", fontsize=12)
    plt.title("Impacto na Latência (Overhead de Segurança)", fontsize=14, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "latencia_boxplot.png"), dpi=300)
    plt.close()

    print(f"Gráficos gerados com sucesso na pasta {output_dir}/")

if __name__ == "__main__":
    main()
