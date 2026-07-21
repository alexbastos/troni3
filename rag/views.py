import json
from django.http import JsonResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# IMPORTANTE: Importe aqui a lógica real do seu RAG para gerar a resposta
# Exemplo: from .pipeline import seu_metodo_de_resposta

@method_decorator(csrf_exempt, name='dispatch') # Remove o erro 403 CSRF para chamadas de API
class ChatRagAPIView(View):
    def post(self, request, *args, **kwargs):
        try:
            # 1. Ler o JSON enviado pelo index.js ou pelo script de teste
            dados = json.loads(request.body)
            pergunta = dados.get("user_query", "")
            llm_puro = dados.get("llm_puro", False)

            if not pergunta:
                return JsonResponse({"error": "O campo 'user_query' é obrigatório."}, status=400)

            # 2. Chamar a sua lógica que busca no Qdrant e responde via LLM
            # (Substitua a linha abaixo pela integração real do seu projeto)
            resposta_do_modelo = f"Processando a pergunta '{pergunta}' através do RAG..."

            # 3. Retornar no formato exato que o frontend e o teste esperam
            return JsonResponse({"answer": resposta_do_modelo})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato JSON inválido."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Erro no servidor: {str(e)}"}, status=500)