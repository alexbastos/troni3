import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"Aviso: Arquivo {filepath} não encontrado.")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    # Caminhos padrão
    antes_path = "../experiments/basic/scientific_evaluation.json"
    depois_path = "../experiments/DD_DLS/scientific_evaluation_backup.json"
    
    # Criar diretório de saída
    output_dir = "experiments/comparativo_evolucao"
    os.makedirs(output_dir, exist_ok=True)
    
    # Carregar dados
    data_antes = load_json(antes_path)
    data_depois = load_json(depois_path)
    
    if not data_antes or not data_depois:
        print("Erro: Não foi possível carregar os dados de 'antes' ou 'depois'. Certifique-se de que os arquivos existem.")
        return

    # Usar tema científico e elegante do seaborn
    sns.set_theme(style="whitegrid")
    
    # === FONTES GLOBALMENTE AMPLIADAS ===
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 14,             # Aumentado de 11 para 14
        'axes.labelsize': 15,        # Aumentado de 12 para 15
        'axes.titlesize': 17,        # Aumentado de 14 para 17
        'xtick.labelsize': 13,       # Aumentado de 10 para 13
        'ytick.labelsize': 13,       # Aumentado de 10 para 13
        'figure.titlesize': 18       # Aumentado de 16 para 18
    })

    # ==========================================
    # 1. GRÁFICO 1: ASR GERAL (Antes vs Depois)
    # ==========================================
    asr_antes_puro = data_antes["ASR_Geral"]["LLM_Puro"]
    asr_antes_rag = data_antes["ASR_Geral"]["LLM_RAG"]
    
    asr_depois_puro = data_depois["ASR_Geral"]["LLM_Puro"]
    asr_depois_rag = data_depois["ASR_Geral"]["LLM_RAG"]
    
    categories = ['LLM Puro', 'LLM + RAG']
    x = np.arange(len(categories))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(9, 6.5))
    
    # Cores modernas e contrastantes (Antes = Vermelho/Coral, Depois = Azul/Verde seguro)
    rects1 = ax.bar(x - width/2, [asr_antes_puro, asr_antes_rag], width, 
                    label='Antes (Sem Defesas)', color='#E57373', edgecolor='black', alpha=0.9)
    rects2 = ax.bar(x + width/2, [asr_depois_puro, asr_depois_rag], width, 
                    label='Depois (Com Defesas DD_DLS)', color='#4CAF50', edgecolor='black', alpha=0.9)
    
    ax.set_ylabel('Attack Success Rate (ASR) %', fontweight='bold')
    ax.set_title('Evolução do Attack Success Rate (ASR)\nAntes vs. Depois da Implementação das Defesas', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.legend(loc='upper right', prop={'size': 12}) # <--- Legenda aumentada
    
    # Adicionar porcentagens no topo das barras (fonte aumentada)
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 4),  # 4 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontweight='bold', size=12) # <--- Tamanho da fonte 12
            
    autolabel(rects1)
    autolabel(rects2)
    
    plt.tight_layout()
    plot1_path = os.path.join(output_dir, "evolucao_asr_geral.png")
    plt.savefig(plot1_path, dpi=300)
    plt.close()
    print(f"-> Salvo: {plot1_path}")

    # ==========================================
    # 2. GRÁFICO 2: ASR POR CATEGORIA (Antes vs Depois)
    # ==========================================
    cats_antes = data_antes["Stats"]["Categorias_RAG"]
    cats_depois = data_depois["Stats"]["Categorias_RAG"]
    
    cat_names = list(cats_antes.keys())
    
    # Calcular ASR de antes e depois por categoria
    asr_cat_antes = []
    asr_cat_depois = []
    
    for cat in cat_names:
        total_a = cats_antes[cat]["total"]
        vuln_a = cats_antes[cat]["vulneravel_fn"]
        asr_cat_antes.append((vuln_a / total_a) * 100 if total_a > 0 else 0)
        
        total_d = cats_depois.get(cat, {}).get("total", 0)
        vuln_d = cats_depois.get(cat, {}).get("vulneravel_fn", 0)
        asr_cat_depois.append((vuln_d / total_d) * 100 if total_d > 0 else 0)

    x_cat = np.arange(len(cat_names))
    
    fig, ax = plt.subplots(figsize=(10.5, 7)) # <--- Ajustado levemente para acomodar as fontes maiores
    rects_cat1 = ax.bar(x_cat - width/2, asr_cat_antes, width, 
                        label='Antes (Sem Defesas)', color='#EF5350', edgecolor='black', alpha=0.9)
    rects_cat2 = ax.bar(x_cat + width/2, asr_cat_depois, width, 
                        label='Depois (Com Defesas DD_DLS)', color='#66BB6A', edgecolor='black', alpha=0.9)
    
    ax.set_ylabel('ASR (%) no RAG', fontweight='bold')
    ax.set_title('Evolução do ASR por Categoria de Ataque (Cenário RAG)\nComparativo de Resiliência', fontweight='bold', pad=15)
    ax.set_xticks(x_cat)
    ax.set_xticklabels(cat_names, rotation=15, ha='right', fontweight='bold')
    ax.set_ylim(0, 100)
    ax.legend(loc='upper right', prop={'size': 12}) # <--- Legenda aumentada
    
    autolabel(rects_cat1)
    autolabel(rects_cat2)
    
    plt.tight_layout()
    plot2_path = os.path.join(output_dir, "evolucao_asr_categoria.png")
    plt.savefig(plot2_path, dpi=300)
    plt.close()
    print(f"-> Salvo: {plot2_path}")

    # ==========================================
    # 3. GRÁFICO 3: IMPACTO NA LATÊNCIA
    # ==========================================
    lat_antes_rag = [d["LLM_RAG"]["latencia_s"] for d in data_antes.get("Raw_Data", []) if d.get("LLM_RAG", {}).get("latencia_s", 0) > 0]
    lat_depois_rag = [d["LLM_RAG"]["latencia_s"] for d in data_depois.get("Raw_Data", []) if d.get("LLM_RAG", {}).get("latencia_s", 0) > 0]
    
    if lat_antes_rag and lat_depois_rag:
        fig, ax = plt.subplots(figsize=(8.5, 6.5))
        
        # Criar dados estruturados para seaborn boxplot
        latency_data = []
        labels = []
        
        for lat in lat_antes_rag:
            latency_data.append(lat)
            labels.append("Antes (Sem Defesas)")
            
        for lat in lat_depois_rag:
            latency_data.append(lat)
            labels.append("Depois (DD_DLS)")
            
        sns.boxplot(x=labels, y=latency_data, hue=labels, palette=["#EF5350", "#66BB6A"], ax=ax, width=0.5, legend=False)
        
        ax.set_ylabel('Tempo de Resposta (segundos)', fontweight='bold')
        ax.set_title('Impacto do SecureLLMPipeline na Latência (Overhead)', fontweight='bold', pad=15)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Adicionar médias textuais (fonte aumentada para size=13)
        mean_antes = np.mean(lat_antes_rag)
        mean_depois = np.mean(lat_depois_rag)
        ax.text(0, mean_antes, f"Média: {mean_antes:.2f}s", ha='center', va='bottom', color='black', fontweight='bold', size=13, bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.25'))
        ax.text(1, mean_depois, f"Média: {mean_depois:.2f}s", ha='center', va='bottom', color='black', fontweight='bold', size=13, bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.25'))
        
        plt.tight_layout()
        plot3_path = os.path.join(output_dir, "comparativo_latencia.png")
        plt.savefig(plot3_path, dpi=300)
        plt.close()
        print(f"-> Salvo: {plot3_path}")
        
    print("\nTodos os gráficos comparativos foram gerados com sucesso na pasta 'experiments/comparativo_evolucao/'!")

if __name__ == "__main__":
    main()