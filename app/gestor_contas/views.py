from django.shortcuts import render, redirect, get_object_or_404
from .utils import geraSubMenu, atualiza_valores_competencia, grafico_linhas_com_media, grafico_barras_com_media, grafico_pizza, salvar_comprovante_externo, gera_parcelas
                    
from .forms import ContaForm, CompetenciForm, pagar_conta_form, PagarContaComSubvaloresForm, SubvaloresFormSet, TagsForm, GastosGeraisForm
from .models import Conta, Competencia, ContaPaga, Subvalores, Parcelamento, Pessoa, Tags, GastosGerais
from django.contrib import messages
from django.urls import reverse
import datetime
import logging  

logger = logging.getLogger(__name__)


# Create your views here.
def index(request):
    return render(request, 'gestor_contas/index.html')

def administracao(request):

    competencias = Competencia.objects.all()

    atualiza_valores_competencia()

    context = {
        'submenu': geraSubMenu('administracao'),
        'title': 'Administração',
        'competencias': competencias,	
    }

    return render(request, 'gestor_contas/administracao.html' , context)

def pagamentos(request):

    competencias = Competencia.objects.filter(ativa=True)

    context = {
        'submenu': geraSubMenu('pagamentos'),
        'title': 'Pagamentos',
        'competencias': competencias,
    }

    return render(request, 'gestor_contas/pagamentos.html' , context)

def contas_mensais(request, id):
    
    competencia = Competencia.objects.get(id=id)
    contas_pagas = ContaPaga.objects.filter(competencia=competencia)
    contas_apagar = Conta.objects.filter(mensal=True, ativa=True).exclude(id__in=contas_pagas.values_list('conta', flat=True))
    contas_exporadicas = Conta.objects.filter(mensal=False, ativa=True, parcelas=False)
    contas_parceladas = Conta.objects.filter(ativa=True, parcelas=True)

    context = {
        'submenu': geraSubMenu('pagamentos'),
        'title': 'Contas Mensais',
        'competencia':competencia,
        'contas_apagar':   contas_apagar,
        'contas_pagas': contas_pagas,
        'contas_exporadicas': contas_exporadicas,
        'contas_parceladas': contas_parceladas,
    }
    return render(request, 'gestor_contas/contas_mensais.html', context)

def pagar_conta_subvalor(request, conta_id, competencia_id):
    logger.info(f"Entrou na função pagar_conta_subvalor com conta_id={conta_id} e competencia_id={competencia_id}")
    conta = get_object_or_404(Conta, id=conta_id)
    competencia = get_object_or_404(Competencia, id=competencia_id)
    
    if request.method == 'POST':
        logger.info(f"Recebido POST com os seguintes dados: {request.POST}")
        form = PagarContaComSubvaloresForm(request.POST, request.FILES, conta=conta, competencia=competencia)
        
        # Se a conta tiver a opção de subvalor ativada, processar o formset
        if conta.subvalor:
            logger.info("Conta tem subvalor ativado. Processando formset.")
            formset = SubvaloresFormSet(request.POST, instance=conta)
            if form.is_valid() and formset.is_valid():
                logger.info("Formulário e formset válidos. Salvando...")
                # Salvar o pagamento
                pagamento = form.save(commit=False)
                pagamento.conta = conta
                pagamento.competencia = competencia
                

                comprovante_uploaded_file = request.FILES.get('comprovante')
                logger.info(f'Recebeu o comprovante: {comprovante_uploaded_file}')
                if comprovante_uploaded_file:
                    logger.info(f'Recebeu o comprovante')

                    path_comprovante = salvar_comprovante_externo(pagamento.data_pagamento ,comprovante_uploaded_file)
                    pagamento.comprovante = path_comprovante
                # Salvar os subvalores
                
                pagamento.save()

                try:
                    formset.save()
                except Exception as e:
                    messages.error(request, f'Erro ao salvar os subvalores: {str(e)}')
                    return redirect('gestor_contas:pagar_conta_subvalor', conta_id=conta_id, competencia_id=competencia_id)
                
                messages.success(request, 'Pagamento registrado com sucesso!')
                return redirect('gestor_contas:contas_mensais', id=competencia_id)
        else:
            logger.info("Conta não tem subvalor ativado. Processando form normal.")
            if form.is_valid():
                logger.info("Formulário válido. Salvando...")
                pagamento = form.save(commit=False)
                pagamento.conta = conta
                pagamento.competencia = competencia
                pagamento.save()

                comprovante_uploaded_file = request.FILES.get('comprovante')
                logger.info(f'Recebeu o comprovante: {comprovante_uploaded_file}')

                if comprovante_uploaded_file:
                    logger.info(f'Recebeu o comprovante')

                    path_comprovante = salvar_comprovante_externo(pagamento.data_pagamento ,comprovante_uploaded_file)
                    pagamento.comprovante = path_comprovante
                    pagamento.save()
                else:

                    logger.info(f'Não recebeu o comprovante')
                    pagamento.save()                
                
                messages.success(request, 'Pagamento registrado com sucesso!')
                return redirect('gestor_contas:contas_mensais', id=competencia_id)
    else:
        form = PagarContaComSubvaloresForm(conta=conta, competencia=competencia, initial={
            'data_pagamento': datetime.date.today(),
        })
        
        # Se a conta tiver a opção de subvalor ativada, criar o formset
        if conta.subvalor:
            formset = SubvaloresFormSet()
        else:
            formset = None
    
    context = {
        'submenu': geraSubMenu('pagamentos'),
        'title': 'Pagar Conta',
        'conta': conta,
        'competencia': competencia,
        'form': form,
        'formset': formset,
        'tem_subvalor': conta.subvalor
    }
    
    return render(request, 'gestor_contas/pagar_conta_subvalor.html', context)

def pagar_conta(request, conta_id,  competencia_id, ):
    logger.info(f'Pagamento de contas')
    if request.method == 'POST':
        logger.info(f'Recebe dados do formulário')
        form = pagar_conta_form(request.POST, request.FILES)
        if form.is_valid():
            logger.info(f'Formulario valido')
            conta = form.cleaned_data['conta']
            competencia = form.cleaned_data['competencia']
            conta_paga = ContaPaga()
            conta_paga.competencia = competencia
            conta_paga.data_pagamento = form.cleaned_data['data_pagamento']
            conta_paga.valor_pago = form.cleaned_data['valor_pago']
            conta_paga.observacoes = form.cleaned_data['observacoes']
            conta_paga.conta = conta

            try:

                logger.info(f'Salvando conta paga')
                conta_paga = form.save(commit=False)
                conta = get_object_or_404(Conta, id=conta_id)
                competencia = get_object_or_404(Competencia, id=competencia_id)
                
                comprovante_uploaded_file = request.FILES.get('comprovante')
                logger.info(f'Recebeu o comprovante: {comprovante_uploaded_file}')

                if comprovante_uploaded_file:
                    logger.info(f'Salvando o comprovante')
                    path_comprovante = salvar_comprovante_externo(conta_paga.data_pagamento ,comprovante_uploaded_file)
                    conta_paga.comprovante = path_comprovante
                    conta_paga.save()
                else:
                    logger.info(f'Não recebeu o comprovante')
                    conta_paga.save()

                # retirado pois acho que ta pagando com ou sem validaçao de comprovante
                # conta_paga.conta = conta
                # conta_paga.competencia = competencia
                # conta_paga.save()
                
                if conta.parcelas:
                    parcela_paga = gera_parcelas(conta_paga)
                    if parcela_paga:
                        messages.success(request, 'Conta paga com sucesso! - Parcela atualizada com sucesso!')
                        logger.info(f'Conta paga com sucesso! - NParcela atualizada com sucesso!')
                    else:
                        messages.success(request, 'Conta paga com sucesso! - Não foi possivel atualizar parcela veja log de erro')
                        logger.info(f'Conta paga com sucesso! - Não foi possivel atualizar parcela veja log de erro')
                else:
                    messages.success(request, 'Conta paga com sucesso!')
                    logger.info(f'conta salva')

                return redirect('gestor_contas:contas_mensais', id=competencia_id)
          
            except Exception as e:
                logger.error(f'Erro ao salvar a conta paga: {str(e)}')
                messages.error(request, f'Erro ao salvar a conta paga: {str(e)}')
                return redirect('gestor_contas:pagar_conta', conta_id=conta_id, competencia_id=competencia_id)
        else:
            logger.warning(f'Formulário inválido: {form.errors}')
            messages.error(request, 'Erro no formulário. Verifique os dados.')
            # Re-renderiza o formulário com erros para o usuário
            conta = get_object_or_404(Conta, id=conta_id)
            competencia = get_object_or_404(Competencia, id=competencia_id)
            context = {
                'submenu': geraSubMenu('pagamentos'),
                'title': 'Pagar Conta',
                'conta': conta,
                'competencia': competencia,
                'form' : form, # Passe o formulário com erros de volta
            }
            return render(request, 'gestor_contas/pagar_conta.html', context)
    
    else:
        form = pagar_conta_form()

    conta = get_object_or_404(Conta, id=conta_id)
    competencia = get_object_or_404(Competencia, id=competencia_id)
    form = pagar_conta_form(instance=ContaPaga(conta=conta, competencia=competencia))

    context = {
        'submenu': geraSubMenu('pagamentos'),
        'title': 'Pagar Conta',
        'conta': conta,
        'competencia': competencia,
        'form' : form,
    }

    return render(request, 'gestor_contas/pagar_conta.html', context)

def editar_conta_pagar(request, conta_id, competencia_id):
    conta_paga = get_object_or_404(ContaPaga, id=conta_id)
    competencia = get_object_or_404(Competencia, id=competencia_id)


    if conta_paga.conta.subvalor:

        form = PagarContaComSubvaloresForm(conta=conta_paga.conta, competencia=competencia, initial={
            'data_pagamento': datetime.date.today(), 'valor_pago': conta_paga.valor_pago, 'observacoes': conta_paga.observacoes
        })

        subvalores = Subvalores.objects.filter(conta=conta_paga.conta)

        if subvalores:
            formset = SubvaloresFormSet(initial={'nome': [subvalor.nome for subvalor in subvalores], 'valor': [subvalor.valor for subvalor in subvalores]})
        else:
            formset = None
    
        context = {
            'submenu': geraSubMenu('pagamentos'),
            'title': 'Pagar Conta',
            'conta': conta_paga.conta,
            'competencia': competencia,
            'form': form,
            'formset': formset,
            'tem_subvalor': conta_paga.conta.subvalor
        }
        return render(request, 'gestor_contas/pagar_conta_subvalor.html', context)
    else:
        form = pagar_conta_form(instance=conta_paga)
        conta = conta_paga.conta

        context = {
        'submenu': geraSubMenu('pagamentos'),
        'title': 'Pagar Conta',
        'conta': conta,
        'competencia': competencia,
        'form' : form,
    }

        return render(request, 'gestor_contas/pagar_conta.html', context)

def contasadmin(request):
    contas_cadastradas = Conta.objects.all().filter(ativa=True)
    context = {
        'submenu': geraSubMenu('administracao'),
        'title': 'Contas Cadastradas',
        'contas_cadastradas': contas_cadastradas,
    }
    return render(request, 'gestor_contas/contasadmin.html', context)

def competenciaadm(request):
    context = {
        'submenu': geraSubMenu('administracao'),
        'title': 'Competências Cadastradas',
    }

    return render(request, 'gestor_contas/competenciaadm.html', context)

def cadastro_competencia(request):

    form = CompetenciForm()

    if request.method == 'POST':
        form = CompetenciForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Competência cadastrada com sucesso!')
            return redirect('gestor_contas:cadastro_conta')
        else:
            messages.error(request, 'Erro ao cadastrar competência.')
            return redirect('gestor_contas:cadastro_competencia')

    context = {
        'submenu': geraSubMenu('cadastro'),
        'title': 'Cadastro de Competência',
        'form': form,	
    }

    return render(request, 'gestor_contas/cadastro_competencia.html', context)

def altera_status(request, id):
    print('altera status')
    pagina_origem = request.POST.get('pagina')
    tipo = request.POST.get('tipo') 
    obj = ''
    print(tipo)
    if tipo == 'conta':
        print('conta')
        obj = get_object_or_404(Conta, id=id)
    if tipo == 'competencia':
        print('competencia')
        obj = get_object_or_404(Competencia, id=id)

    if obj:
        print(obj)
        obj.ativa = not obj.ativa
        obj.save()

    return redirect(reverse(f'gestor_contas:{pagina_origem}'))

def cadastro_conta(request):
    contas_cadastradas = Conta.objects.all()
    # contas_embutidas = ContaEmbutida.objects.all()

    context = {
        'submenu': geraSubMenu('cadastro'),
        'title': 'Cadastro de Contas',
        'subtitle': 'Contas Cadastradas',
        'contas_cadastradas': contas_cadastradas,
        # 'contas_embutidas': contas_embutidas,
    }

    return render(request, 'gestor_contas/cadastro_conta.html', context)

def cadastro_contas(request):
    contas_cadastradas = Conta.objects.all().filter(ativa=True)
    if request.method == 'POST':
        form = ContaForm(request.POST)
        if form.is_valid():
            nome_conta = form.cleaned_data['nome'].lower()  # Converter para minúsculas
            
            if form.cleaned_data['parcelas']:
                if form.cleaned_data['mensal'] or form.cleaned_data['subvalor']:
                    messages.error(request, 'Uma conta Parcelada não pode ser Mensal ou ter Subvalor ao mesmo tempo.')
                    context = {
                        'submenu': geraSubMenu('cadastro'),
                        'title': 'Cadastro de Contas',
                        'form': form,
                        'contas_cadastradas': contas_cadastradas,
                    }
                    return render(request, 'gestor_contas/cadastro_contas.html', context)
                else:
                    if form.cleaned_data['qtd_parcelas'] <= 1 or form.cleaned_data['valor_total'] < 0:
                        messages.error(request, 'A quantidade de parcelas deve ser maior que 1 e o valor total deve ser maior que 0.')
                        context = {
                            'submenu': geraSubMenu('cadastro'),
                            'title': 'Cadastro de Contas',
                            'form': form,
                            'contas_cadastradas': contas_cadastradas,
                        }
                        return render(request, 'gestor_contas/cadastro_contas.html', context)


            if Conta.objects.filter(nome=nome_conta, ativa=True).exists():
                messages.error(request, 'Já existe uma conta ativa com este nome.')
                context = {
                    'submenu': geraSubMenu('cadastro'),
                    'title': 'Cadastro de Contas',
                    'form': form,
                    'contas_cadastradas': contas_cadastradas,
                }
                return render(request, 'gestor_contas/cadastro_contas.html', context)
            conta = form.save(commit=False)
            conta.nome = nome_conta  # Atribuir o nome em minúsculas
            conta.save()
            messages.success(request, 'Conta cadastrada com sucesso!')
            return redirect('gestor_contas:cadastro_conta')  # Redirecionar para uma página de sucesso
        else:
            # Se o formulário não for válido, vamos mostrá-lo novamente com os erros
            context = {
                'submenu': geraSubMenu('cadastro'),
                'title': 'Cadastro de Contas',
                'form': form,
            }
            return render(request, 'gestor_contas/cadastro_contas.html', context)
    else:
        form = ContaForm()
        context = {
            'submenu': geraSubMenu('cadastro'),
            'title': 'Cadastro de Contas',
            'form': form,
            'contas_cadastradas': contas_cadastradas,
        }
        return render(request, 'gestor_contas/cadastro_contas.html', context)

def relatorios(request):

    atualiza_valores_competencia()

    context = {
        'submenu': geraSubMenu('relatorios'),
        'title': 'Relatórios',
    }
    return render(request, 'gestor_contas/relatorios.html', context) 

def relatorio_meses(request):

    competencias = Competencia.objects.all().order_by('ano','mes')
    grafico = False

    if request.method == 'POST':
        competencia_select = request.POST.getlist('competencia')
        competencia_select = Competencia.objects.filter(id__in=competencia_select)

        meses = []
        valor_total = []
        for competencia in competencia_select:
            meses.append(f'{competencia.mes}/{competencia.ano}')
            valor_total.append(competencia.total_pago)

        print(meses)
        print(valor_total)

        grafico = grafico_linhas_com_media(meses, valor_total, 'Meses', 'Valor Total', 'Meses')
        print(grafico)

    context = {
        'submenu': geraSubMenu('relatorios'),
        'title': 'Relatório de meses',
        'competencias' : competencias,
        'grafico': grafico,	
    }
    return render(request, 'gestor_contas/relatorio_meses.html', context)

def relatorio_contas(request):
    
    if request.method == 'POST':
        contas_select = request.POST.get('conta')
        conta =    Conta.objects.get(id=contas_select)
        contas_pagas_select = ContaPaga.objects.filter(conta=conta)



        meses=[]
        valores=[]
        for contas_pagas in contas_pagas_select:
            meses.append(f'{contas_pagas.competencia.mes}/{contas_pagas.competencia.ano}')
            valores.append(contas_pagas.valor_pago)
        
        grafico = grafico_barras_com_media(meses, valores, 'Meses', 'Valor', 'Meses')
        subtitulo = f'Contas pagas da conta {conta.nome.upper()}'
    else:
        grafico = False
        subtitulo = False
        


    contas = Conta.objects.all()
    context = {
        'submenu': geraSubMenu('relatorios'),
        'title': 'Relatório de Contas',
        'subtitle': subtitulo,
        'contas': contas,
        'grafico': grafico,	
    }
    return render(request, 'gestor_contas/relatorio_contas.html', context)

def relatorio_competencia(request):
    
    if request.method == 'POST':
        competencia = request.POST.get('competencia')
        competencias = Competencia.objects.filter(id=competencia)
        contas_pagas = ContaPaga.objects.filter(competencia=competencia)
        
        itens = []
        valores = []

        for conta_paga in contas_pagas:
            itens.append(f'{conta_paga.conta.nome.upper()}')
            valores.append(conta_paga.valor_pago)
    

    #a somar os valores dos gastos de gerais e tirar o que nao e de credito
        gastos_gerais = GastosGerais.objects.filter(competencia=competencia, contabiliza=True)
        if gastos_gerais:
            total_geral = 0
            for gasto_geral in gastos_gerais:
                total_geral +=  gasto_geral.valor
            print(total_geral)
            
            valores.append(total_geral)
            itens.append('Gastos Gerais')



        subtitulo = False
        titulo = ''
        for competencia in competencias:
            titulo = f'Relatório da competencia {competencia.mes}/{competencia.ano}'
            subtitulo = f'Contas pagas da competencia {competencia.mes}/{competencia.ano}'
       

        grafico = grafico_pizza(valores, itens, titulo)

 
        
    else:
        grafico = False
        subtitulo = False
        


    competencias = Competencia.objects.all()

    context = {
        'submenu': geraSubMenu('relatorios'),
        'title': 'Relatório de Competencias',
        'subtitle': subtitulo,
        'competencias': competencias,
        'grafico': grafico,	
    }
    return render(request, 'gestor_contas/relatorio_competencia.html', context)

def contas_pagas(request):
    logger.info('Entrou na função contas_pagas')
    competencias = Competencia.objects.all()
    contas =  Conta.objects.all()

    if request.method == 'POST':
        logger.info('Entrou no if do POST')
        competencia_select = request.POST.get('competencia')
        logger.info(f'Competencia selecionada: {competencia_select}')
        if competencia_select != 'False':
            competencia = Competencia.objects.get(id=competencia_select)
        else:
            competencia = False

        conta_select = request.POST.get('conta')
        logger.info(f'Conta selecionada: {conta_select}')
        if conta_select != 'False':
            conta = Conta.objects.get(id=conta_select)
        else:
            conta = False


        if competencia:
            if conta:
                contas_pagas = ContaPaga.objects.filter(competencia=competencia, conta=conta)
            else:
                contas_pagas = ContaPaga.objects.filter(competencia=competencia)
        else:
            contas_pagas = ContaPaga.objects.filter(conta=conta)
        
        ids_contas_pagas = [conta_paga.id for conta_paga in contas_pagas]


        #calcula o valor tota ja pago
        if competencia_select == 'False':
            parcelamento = Parcelamento.objects.filter(conta_paga_id__in=ids_contas_pagas)
            if parcelamento:
                valor_total_pago = 0
                parcelamentoa_totais = {}
                for parcela in parcelamento:
                    valor_total_pago += parcela.valor_pago

                parcelamentoa_totais['total_pago']= valor_total_pago
                parcelamentoa_totais['parcelas_pagas'] = parcelamento.count() 
            else:
                parcelamentoa_totais = False
        else:
            parcelamento = False
            parcelamentoa_totais = False

    else:
        contas_pagas = False
        parcelamento = False
        parcelamentoa_totais = False

    context ={
        'submenu': geraSubMenu('pagamentos'),
        'title': 'Contas Pagas',
        'competencias': competencias,
        'contas': contas,
        'contas_pagas': contas_pagas, 
        'parcelamento': parcelamento,
        'parcelamentoa_totais': parcelamentoa_totais,
    }

    return render(request, 'gestor_contas/contas_pagas.html', context)

def cadastra_tag(request):
    form = TagsForm(request.POST or None)
    tags = Tags.objects.all()
    print(tags)

    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Tag cadastrada com sucesso')
                return redirect('gestor_contas:cadastra_tag')
            except Exception as e:
                logger.error(f'Erro ao cadastrar tag: {e}')
                messages.error(request, 'Erro ao cadastrar tag')
                return redirect('gestor_contas:cadastra_tag')

    context = {
        'submenu': geraSubMenu('cadastros'),
        'title': 'Cadastro de Tags',
        'form': form,
        'tags': tags,
    }

    return render(request, 'gestor_contas/cadastra_tag.html', context)

def gastos_gerais(request):

    form = GastosGeraisForm()

    if request.method == 'POST':
        form = GastosGeraisForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Gasto cadastrado com sucesso')
                return redirect('gestor_contas:gastos_gerais')
            except Exception as e:
                logger.error(f'Erro ao cadastrar gasto geral: {e}')
                messages.error(request, 'Erro ao cadastrar gasto geral')
                return redirect('gestor_contas:gastos_gerais')

    context = {
        'submenu': geraSubMenu('gastos_gerais'),
        'title': 'Gastos Gerais',
        'form': form,
    }

    return render(request, 'gestor_contas/gastos_gerais.html', context)

def gastos_gerais_relat(request):

    def buscas_gastos(competencia_select, tag_select, pessoa_select):
        if competencia_select:
            if tag_select:
                if pessoa_select:
                    gastos_gerais = GastosGerais.objects.filter(competencia=competencia_select, tags=tag_select, pessoa=pessoa_select).order_by('data_compra')
                else:
                    gastos_gerais = GastosGerais.objects.filter(competencia=competencia_select, tags=tag_select).order_by('data_compra')
            else:
                if pessoa_select:
                    gastos_gerais = GastosGerais.objects.filter(competencia=competencia_select, pessoa=pessoa_select).order_by('data_compra')
                else:
                    gastos_gerais = GastosGerais.objects.filter(competencia=competencia_select).order_by('data_compra')
        else: 
                if tag_select:
                    if pessoa_select:
                        gastos_gerais = GastosGerais.objects.filter(tags=tag_select, pessoa=pessoa_select).order_by('data_compra')
                    else:
                        gastos_gerais = GastosGerais.objects.filter(tags=tag_select).order_by('data_compra')
                else:
                    if pessoa_select:
                        gastos_gerais = GastosGerais.objects.filter(pessoa=pessoa_select).order_by('data_compra')
        return gastos_gerais

    competencias = Competencia.objects.all()
    tags = Tags.objects.all()
    pessoas = Pessoa.objects.all()

    if request.method == 'POST':
        try:
            competencia_select = get_object_or_404(Competencia, id=request.POST.get('competencia'))    
        except:
            competencia_select = False
        try:
            tag_select = get_object_or_404(Tags, id=request.POST.get('tag'))
        except:
            tag_select = False
        
        try:
            pessoa_select = get_object_or_404(Pessoa, id=request.POST.get('pessoa'))
        except:
            pessoa_select = False
        
        # if competencia_select:
        #     if tag_select:
        #         if pessoa_select:
        #             gastos_gerais = GastosGerais.objects.filter(competencia=competencia_select, tags=tag_select, pessoa=pessoa_select)
        #         else:
        #             gastos_gerais = GastosGerais.objects.filter(competencia=competencia_select, tags=tag_select)
        #     else:
        #         if pessoa_select:
        #             gastos_gerais = GastosGerais.objects.filter(competencia=competencia_select, pessoa=pessoa_select)
        #         else:
        #             gastos_gerais = GastosGerais.objects.filter(competencia=competencia_select)
        # else: 
        #         if tag_select:
        #             if pessoa_select:
        #                 gastos_gerais = GastosGerais.objects.filter(tags=tag_select, pessoa=pessoa_select)
        #             else:
        #                 gastos_gerais = GastosGerais.objects.filter(tags=tag_select)
        #         else:
        #             if pessoa_select:
        #                 gastos_gerais = GastosGerais.objects.filter(pessoa=pessoa_select)

        gastos_gerais = buscas_gastos(competencia_select, tag_select, pessoa_select)

                    
        total = 0
        valores =[]
        itens = []

        all_tags = Tags.objects.all()
        print("Nomes das Tags:")
        for tag in all_tags: # Itera sobre cada tag
            nome_tag = tag.nome
            tagvalor = 0

            for gastos in gastos_gerais: # Itera sobre cada gasto
                total += gastos.valor
                for tag_gasto in gastos.tags.all(): # Itera sobre cada tag do gasto
                    if tag_gasto.nome == tag.nome:
                       tagvalor += gastos.valor

            if tagvalor > 0:
                itens.append(nome_tag)
                valores.append(tagvalor)
                        
                                     
        print(valores)
        print(itens)

        grafico = grafico_pizza(valores, itens, 'Gastos por tags', )
        

    else:
        gastos_gerais = False
        total = False
        grafico = False



    context = {
        'submenu': geraSubMenu('gastos_gerais'),
        'title': 'Relatório de Gastos Gerais',
        'competencias': competencias,
        'tags': tags,
        'gastos_gerais': gastos_gerais,
        'total': total,
        'grafico': grafico,
        'pessoas': pessoas,

    }

    return render(request, 'gestor_contas/gastos_gerais_relat.html', context)