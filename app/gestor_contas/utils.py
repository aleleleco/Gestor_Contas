from .models import Submenu, Competencia, ContaPaga
import matplotlib.pyplot as plt
import os
from django.conf import settings
import numpy as np
import logging  

logger = logging.getLogger(__name__)


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
    

def grafico_barras_com_media(valx, valy, titlex, titley, title, nome_arquivo="grafico_barras.png"):
    """
    Gera um gráfico de barras com uma linha média.

    Args:
        valx (list): Lista de valores para o eixo x (e.g., nomes, categorias).
        valy (list): Lista de valores numéricos para o eixo y.
        titlex (str): Título para o eixo x.
        titley (str): Título para o eixo y.
        title (str): Título do gráfico.
        nome_arquivo (str, opcional): Nome do arquivo para salvar o gráfico.
                                       Padrão é "grafico_barras.png".

    Returns:
        str: Caminho completo para o arquivo da imagem do gráfico gerado.
             Retorna None em caso de erro.
    """
    try:
        # 1. Criar a figura e os eixos
        plt.figure(figsize=(10, 6))  # Define o tamanho da figura
        plt.bar(valx, valy, color='skyblue')  # Cria o gráfico de barras

        # 2. Calcular a linha média
        media = np.mean(valy)
        plt.axhline(y=media, color='red', linestyle='--', label=f'Média: {media:.2f}')  # Adiciona a linha média

        # 3. Adicionar rótulos e título
        plt.xlabel(titlex)
        plt.ylabel(titley)
        plt.title(title)
        plt.grid(axis='y', alpha=0.75)  # Adiciona grade no eixo y para facilitar a leitura
        plt.legend()
        plt.xticks(rotation=45, ha='right')  # Rotaciona os rótulos do eixo x para melhor visualização
        plt.tight_layout()  # Ajusta o layout para evitar cortes

        # 4. Salvar o gráfico em um arquivo
        caminho_pasta_media = os.path.join(settings.MEDIA_ROOT, 'graficos')
        os.makedirs(caminho_pasta_media, exist_ok=True)
        caminho_arquivo = os.path.join(caminho_pasta_media, nome_arquivo)
        plt.savefig(caminho_arquivo)
        plt.close()  # Fecha a figura para liberar memória

        return os.path.join('graficos', nome_arquivo)  # Retorna o caminho relativo para o arquivo

    except Exception as e:
        print(f"Erro ao gerar o gráfico de barras: {e}")
        return None
    
def salvar_comprovante_externo(data_pagamento, comprovante_file):
    
    if not comprovante_file:
        logger.warning("Nenhum arquivo de comprovante fornecido para salvar_comprovante_externo.")
        return None
    
    if not data_pagamento:
        logger.warning("Nenhuma data de pagamento fornecida para salvar_comprovante_externo.")
        return None

    meses_pt = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril', 5: 'maio', 6: 'junho',
        7: 'julho', 8: 'agosto', 9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    
    ano = str(data_pagamento.year)
    mes_num = f'{data_pagamento.month:02d}'
    nome_mes = meses_pt[data_pagamento.month]

    # Caminho base do .env (C:/Users/PC-Leleco/Dropbox/Pessoal/ContasPagas)
    base_dir_comprovantes = settings.COMPROVANTES_BASE_DIR
    
    # Caminho completo da pasta onde o arquivo será salvo
    caminho_destino_pasta = os.path.join(base_dir_comprovantes, ano, f'{mes_num}-{nome_mes}')
    
    logger.info(f"Tentando criar pasta de destino: {caminho_destino_pasta}")
    try:
        os.makedirs(caminho_destino_pasta, exist_ok=True)
        logger.info(f'Pasta de destino verificada/criada: {caminho_destino_pasta}')
    except OSError as e:
        logger.error(f"Erro ao criar a pasta de destino '{caminho_destino_pasta}': {e}")
        return None
    
    nome_arquivo_destino = comprovante_file.name
    caminho_completo_arquivo = os.path.join(caminho_destino_pasta, nome_arquivo_destino)
    
    logger.info(f"Salvando arquivo em: {caminho_completo_arquivo}")
    try:
        with open(caminho_completo_arquivo, 'wb+') as destination:
            for chunk in comprovante_file.chunks():
                destination.write(chunk)
        logger.info(f"Arquivo '{nome_arquivo_destino}' salvo com sucesso em '{caminho_completo_arquivo}'")
        
        # O valor salvo no banco deve ser o caminho relativo ao MEDIA_ROOT (se for para ser servido pelo Django)
        # Ou o caminho absoluto se não for servido pelo Django.
        # Se MEDIA_ROOT está para o projeto, e este arquivo está FORA, você não pode usar o MEDIA_URL para servi-lo.
        # Nesse caso, salve o caminho COMPLETO no banco de dados.
        return caminho_completo_arquivo # Retorna o caminho absoluto do arquivo salvo
    except IOError as e:
        logger.error(f"Erro de E/S ao salvar o arquivo: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao salvar o arquivo: {e}")
        return None