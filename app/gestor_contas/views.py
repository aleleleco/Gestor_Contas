from django.shortcuts import render, redirect, get_object_or_404
from .utils import geraSubMenu
from .forms import ContaForm, ContaEmbutidaForm
from .models import Conta, ContaEmbutida
from django.contrib import messages
from django.urls import reverse


# Create your views here.
def index(request):
    return render(request, 'gestor_contas/index.html')

def cadastro_competencia(request):

    context = {
        'submenu': geraSubMenu('cadastro'),
        'title': 'Cadastro de Competência',
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
    if tipo == 'conta_embutida':
        print('conta embutida')
        obj = get_object_or_404(ContaEmbutida, id=id)

    if obj:
        print(obj)
        obj.ativa = not obj.ativa
        obj.save()

    return redirect(reverse(f'gestor_contas:{pagina_origem}'))


def cadastro_conta(request):
    contas_cadastradas = Conta.objects.all()
    contas_embutidas = ContaEmbutida.objects.all()

    context = {
        'submenu': geraSubMenu('cadastro'),
        'title': 'Cadastro de Contas',
        'subtitle': 'Contas Cadastradas',
        'contas_cadastradas': contas_cadastradas,
        'contas_embutidas': contas_embutidas,
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
    
def cadastro_contas_embutidas(request):
    contas_cadastradas = ContaEmbutida.objects.all().filter(ativa=True)
    if request.method == 'POST':
        form = ContaEmbutidaForm(request.POST)
        if form.is_valid():
            nome_conta = form.cleaned_data['nome'].lower()  # Converter para minúsculas
           
            if ContaEmbutida.objects.filter(nome=nome_conta, ativa=True).exists():
                messages.error(request, 'Já existe uma conta ativa com este nome.')
                context = {
                    'submenu': geraSubMenu('cadastro'),
                    'title': 'Cadastro de Contas embutidas',
                    'form': form,
                    'contas_cadastradas': contas_cadastradas,
                }
                return render(request, 'gestor_contas/cadastro_contas_embutidas.html', context)
            
            conta = form.save(commit=False)
            conta.nome = nome_conta  # Atribuir o nome em minúsculas
            conta.save()
            messages.success(request, 'Conta cadastrada com sucesso!')
            return redirect('gestor_contas:cadastro_conta')  # Redirecionar para uma página de sucesso
        else:
            # Se o formulário não for válido, vamos mostrá-lo novamente com os erros
            context = {
                'submenu': geraSubMenu('cadastro'),
                'title': 'Cadastro de Contas embutidas',
                'form': form,
            }
            return render(request, 'gestor_contas/cadastro_contas_embutidas.html', context)
    else:
        form = ContaForm()
        context = {
            'submenu': geraSubMenu('cadastro'),
            'title': 'Cadastro de Contas embutidas',
            'form': form,
            'contas_cadastradas': contas_cadastradas,
        }
        return render(request, 'gestor_contas/cadastro_contas_embutidas.html', context)