from django.shortcuts import render, redirect, get_object_or_404
from .utils import geraSubMenu, atualiza_valores_competencia, grafico_linhas_com_media, grafico_pizza
from .forms import ContaForm, CompetenciForm, pagar_conta_form, PagarContaComSubvaloresForm, SubvaloresFormSet
from .models import Conta, Competencia, ContaPaga, Subvalores
from django.contrib import messages
from django.urls import reverse
import datetime


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
    contas_exporadicas = Conta.objects.filter(mensal=False, ativa=True)

    context = {
        'submenu': geraSubMenu('pagamentos'),
        'title': 'Contas Mensais',
        'competencia':competencia,
        'contas_apagar':   contas_apagar,
        'contas_pagas': contas_pagas,
        'contas_exporadicas': contas_exporadicas
    }
    return render(request, 'gestor_contas/contas_mensais.html', context)


def pagar_conta_subvalor(request, conta_id, competencia_id):
    conta = get_object_or_404(Conta, id=conta_id)
    competencia = get_object_or_404(Competencia, id=competencia_id)
    
    if request.method == 'POST':
        form = PagarContaComSubvaloresForm(request.POST, request.FILES, conta=conta, competencia=competencia)
        
        # Se a conta tiver a opção de subvalor ativada, processar o formset
        if conta.subvalor:
            formset = SubvaloresFormSet(request.POST, instance=conta)
            if form.is_valid() and formset.is_valid():
                # Salvar o pagamento
                pagamento = form.save(commit=False)
                pagamento.conta = conta
                pagamento.competencia = competencia
                pagamento.save()
                
                # Salvar os subvalores
                try:
                    formset.save()
                except Exception as e:
                    messages.error(request, f'Erro ao salvar os subvalores: {str(e)}')
                    return redirect('gestor_contas:pagar_conta_subvalor', conta_id=conta_id, competencia_id=competencia_id)
                
                
                messages.success(request, 'Pagamento registrado com sucesso!')
                return redirect('gestor_contas:contas_mensais', id=competencia_id)
        else:
            if form.is_valid():
                pagamento = form.save(commit=False)
                pagamento.conta = conta
                pagamento.competencia = competencia
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



def pagar_conta(request, conta_id,  competencia_id):

    if request.method == 'POST':
        form = pagar_conta_form(request.POST)
        if form.is_valid():
            conta = form.cleaned_data['conta']
            competencia = form.cleaned_data['competencia']
            conta_paga = ContaPaga()
            conta_paga.competencia = competencia
            conta_paga.data_pagamento = form.cleaned_data['data_pagamento']
            conta_paga.valor_pago = form.cleaned_data['valor_pago']
            conta_paga.observacoes = form.cleaned_data['observacoes']
            conta_paga.conta = conta
            try:
                conta_paga.save()
            except Exception as e:
                messages.error(request, f'Erro ao salvar a conta paga: {str(e)}')
                return redirect('gestor_contas:pagar_conta', conta_id=conta_id, competencia_id=competencia_id)
            
            messages.success(request, 'Conta paga com sucesso!')
            return redirect('gestor_contas:contas_mensais', id=competencia_id)
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


