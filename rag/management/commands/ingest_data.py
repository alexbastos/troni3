import os
import json
import uuid
import time
from pathlib import Path
from django.core.management.base import BaseCommand
from embeddings_utils import create_embedding
from qdrant_singleton import QdrantSingleton
import pymupdf4llm

qdrant = QdrantSingleton()

DATA_CONFIG_FILE = "data_config.json"
EMBEDDING_DIM = 3072

def chunk_text(text, chunk_size=500, overlap=50):
    """Divide texto em pedaços menores para embeddings"""
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks

def process_txt(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return [{"text": chunk, "page": None} for chunk in chunk_text(text)]

def process_pdf(file_path: Path):
    chunks = pymupdf4llm.to_markdown(str(file_path), page_chunks=True)

    if isinstance(chunks, str):
        return [{"text": str(chunks), "page": None}]

    dataset = []
    for page_num, text in enumerate(chunks, start=1):
        # força conversão para string pura
        dataset.append({
            "text": str(text),
            "page": page_num
        })
    return dataset


class Command(BaseCommand):
    help = "Ingesta dados para Qdrant usando embeddings próprios"

    def handle(self, *args, **options):
        # --- Ler configuração ---
        with open(DATA_CONFIG_FILE, "r", encoding="utf-8") as f:
            data_config = json.load(f)

        for categoria, arquivos in data_config.items():
            print(f"\n📂 Ingestando categoria: {categoria}")
            collection_name = qdrant.ensure_collection(categoria)

            all_points = []
            for arquivo in arquivos:
                path = Path(arquivo)
                if not path.exists():
                    print(f"   ❌ Arquivo não encontrado: {arquivo}")
                    continue

                try:
                    if path.suffix.lower() == ".pdf":
                        docs = process_pdf(path)
                    else:
                        docs = process_txt(path)

                    for d in docs:
                        # Loop de re-tentativa resiliente para lidar com Rate Limits da OpenAI
                        while True:
                            try:
                                embedding = create_embedding(d["text"])
                                point_id = str(uuid.uuid4())
                                all_points.append({
                                    "id": point_id,
                                    "vector": embedding,
                                    "payload": {
                                        "text": d["text"],
                                        "source": path.name,
                                        "page": d["page"],
                                        "categoria": categoria
                                    }
                                })
                                # Pequena pausa padrão em condições normais
                                time.sleep(1.0)
                                break  # Sucesso! Sai do loop 'while' e vai para o próximo chunk
                                
                            except Exception as e:
                                # Captura especificamente erros de limite excedido (Rate Limit 429)
                                if "429" in str(e) or "rate_limit" in str(e):
                                    print(f"   ⚠️ Limite da OpenAI atingido. Aguardando 60 segundos para retomar...")
                                    time.sleep(60.0)
                                    print(f"   🔄 Retomando processamento do trecho...")
                                else:
                                    # Caso seja um erro diferente, lança para interromper o arquivo
                                    raise e

                    print(f"   ✅ {len(docs)} chunks extraídos de {path.name}")

                except Exception as e:
                    print(f"   ❌ Erro ao processar {path.name}: {e}")

            if all_points:
                qdrant.upsert_points(categoria, all_points)
                print(f"🚀 {len(all_points)} pontos inseridos na coleção {collection_name}")
            else:
                print(f"⚠️ Nenhum ponto inserido para {categoria}")

        print("\n🎯 Ingest completo!")