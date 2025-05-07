from .models import Submenu, Competencia, ContaPaga
import matplotlib.pyplot as plt
import os
from django.conf import settings
import numpy as np


def geraSubMenu(pagina):
    submenu = Submenu.objects.filter(pagina=pagina)


    return submenu


def atualiza_valores_competencia():
    print('atualiza_valores_competencia')
    competencias = Competencia.objects.filter(ativa=True)

    for competencia in competencias:
        print(competencia)
        contas = ContaPaga.objects.filter(competencia=competencia)
        valor_total = sum(conta.valor_pago for conta in contas)
        print(valor_total)
        competencia.total_pago = valor_total
        competencia.save()
    

def grafico_linhas_com_media(valx, valy, titlex, titley, title, nome_arquivo="grafico_linha.png"):
    """
    Gera um gráfico de linhas com uma linha média.

    Args:
        meses (list): Lista de strings representando os meses.
        valores (list): Lista de valores numéricos correspondentes aos meses.
        nome_arquivo (str, opcional): Nome do arquivo para salvar o gráfico.
                                       Padrão é "grafico_linha.png".

    Returns:
        str: Caminho completo para o arquivo da imagem do gráfico gerado.
             Retorna None em caso de erro.
    """
    try:
        # 1. Criar a figura e os eixos
        plt.figure(figsize=(10, 6))  # Define o tamanho da figura
        plt.plot(valx, valy, marker='o', linestyle='-', color='blue', label='Valores')

        # 2. Calcular a linha média
        media = np.mean(valy)
        plt.axhline(y=media, color='red', linestyle='--', label=f'Média: {media:.2f}')

        # 3. Adicionar rótulos e título
        plt.xlabel(titlex)
        plt.ylabel(titley)
        plt.title(title)
        plt.grid(True)
        plt.legend()
        plt.xticks(rotation=45, ha='right') # Rotaciona os rótulos do eixo x para melhor visualização
        plt.tight_layout() # Ajusta o layout para evitar cortes

        # 4. Salvar o gráfico em um arquivo
        caminho_pasta_media = os.path.join(settings.MEDIA_ROOT, 'graficos')
        os.makedirs(caminho_pasta_media, exist_ok=True)
        caminho_arquivo = os.path.join(caminho_pasta_media, nome_arquivo)
        plt.savefig(caminho_arquivo)
        plt.close() # Fecha a figura para liberar memória

        return os.path.join('graficos', nome_arquivo) # Retorna o caminho relativo para o arquivo

    except Exception as e:
        print(f"Erro ao gerar o gráfico: {e}")
        return None

def grafico_pizza(valores, itens, title, nome_arquivo="grafico_pizza.png"):
    """
    Gera um gráfico de pizza.

    Args:
        valores (list): Lista de valores numéricos representando as fatias da pizza.
        itens (list): Lista de strings representando os rótulos correspondentes aos valores.
        nome_arquivo (str, opcional): Nome do arquivo para salvar o gráfico.
                                       Padrão é "grafico_pizza.png".

    Returns:
        str: Caminho completo para o arquivo da imagem do gráfico gerado.
             Retorna None em caso de erro.
    """
    try:
        # 1. Criar a figura e os eixos
        plt.figure(figsize=(8, 8)) # Define o tamanho da figura (geralmente quadrado para pizza)
        plt.pie(valores, labels=itens, autopct='%1.1f%%', startangle=140)
        #   - valores: os tamanhos de cada fatia.
        #   - labels: os rótulos de cada fatia.
        #   - autopct: formato para exibir as porcentagens em cada fatia.
        #   - startangle: ângulo inicial da primeira fatia (ajusta a orientação).

        # 2. Adicionar um título
        plt.title(title)

        # 3. Garantir que o círculo seja desenhado como um círculo
        plt.axis('equal')

        # 4. Salvar o gráfico em um arquivo
        caminho_pasta_media = os.path.join(settings.MEDIA_ROOT, 'graficos')
        os.makedirs(caminho_pasta_media, exist_ok=True)
        caminho_arquivo = os.path.join(caminho_pasta_media, nome_arquivo)
        plt.savefig(caminho_arquivo)
        plt.close() # Fecha a figura para liberar memória

        return os.path.join('graficos', nome_arquivo) # Retorna o caminho relativo para o arquivo

    except Exception as e:
        print(f"Erro ao gerar o gráfico de pizza: {e}")
        return None