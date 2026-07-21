import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def plot_asr_comparison(asr_llm, asr_rag):
    # Gráfico de Barras ASR: LLM vs RAG
    labels = ['LLM Puro (Injeção Direta)', 'LLM + RAG (Injeção Indireta)']
    values = [asr_llm, asr_rag]
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, values, color=['#4CAF50', '#F44336'], edgecolor='black')
    
    plt.ylabel('Attack Success Rate (ASR) %', fontsize=12)
    plt.title('Comparativo de Vulnerabilidade:\nLLM Puro vs. Arquitetura RAG', fontsize=14, fontweight='bold')
    plt.ylim(0, max(100, max(values) + 10))
    
    # Adicionar o percentual em cima das barras
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
    plt.tight_layout()
    plt.savefig('asr_comparison.png', dpi=300)
    plt.close()
    print("-> Gráfico de comparação ASR salvo como asr_comparison.png")


def plot_category_breakdown(stats):
    # Gráfico das Categorias no RAG
    categorias_rag = stats.get("Categorias_RAG", {})
    
    labels = []
    protegidos = []
    vulneraveis = []
    
    # Filtra e agrupa as categorias
    for cat, data in categorias_rag.items():
        if data["total"] > 0:
            labels.append(cat)
            protegidos.append(data["protegido_tp"])
            vulneraveis.append(data["vulneravel_fn"])
            
    x = np.arange(len(labels))
    width = 0.6
    
    plt.figure(figsize=(12, 7))
    p1 = plt.bar(x, protegidos, width, label='Protegido (Falha Segura)', color='#2196F3', edgecolor='black')
    p2 = plt.bar(x, vulneraveis, width, bottom=protegidos, label='Vulnerável (Bypass)', color='#FF9800', edgecolor='black')
    
    plt.ylabel('Número de Amostras', fontsize=12)
    plt.title('Resiliência do RAG por Categoria de Ataque', fontsize=14, fontweight='bold')
    plt.xticks(x, labels, rotation=45, ha='right', fontsize=10)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.tight_layout()
    plt.savefig('category_breakdown.png', dpi=300)
    plt.close()
    print("-> Gráfico de resiliência por categoria salvo como category_breakdown.png")

if __name__ == "__main__":
    if not os.path.exists("scientific_evaluation.json"):
        print("Erro: Arquivo scientific_evaluation.json não encontrado. Execute o teste científico primeiro.")
        exit(1)
        
    with open("scientific_evaluation.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    asr_llm = data.get("ASR_Geral", {}).get("LLM_Puro", 0)
    asr_rag = data.get("ASR_Geral", {}).get("LLM_RAG", 0)
    stats = data.get("Stats", {})
    
    # Utilizar Seaborn para estilo de publicação
    sns.set_theme(style="whitegrid")
    
    plot_asr_comparison(asr_llm, asr_rag)
    plot_category_breakdown(stats)
    
    print("Todos os gráficos foram gerados com sucesso!")
