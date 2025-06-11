from django import forms
from .models import Conta, Competencia, ContaPaga, Subvalores
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime
from django.forms import formset_factory, inlineformset_factory


class ContaForm(forms.ModelForm):
    data_vencimento = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
        label="Dia de Vencimento"
    )

    class Meta:
        model = Conta
        fields = ['nome', 'data_vencimento', 'observacoes', 'ativa', 'mensal', 'subvalor']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'mensal': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'subvalor': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'border-color: #ced4da; box-shadow: none;'}),                    
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Remove o ":" padrão das labels
        self.fields['ativa'].label = "Conta Ativa" # Define o label do checkbox


class pagar_conta_form(forms.ModelForm):
    
    class Meta:
        model = ContaPaga
        fields = ['competencia','data_pagamento', 'valor_pago', 'comprovante', 'observacoes', 'conta']
        widgets = {
            'competencia': forms.Select(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'data_pagamento': forms.DateInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'valor_pago': forms.NumberInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'comprovante': forms.FileInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'conta': forms.Select(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
        }

class CompetenciForm(forms.ModelForm):
    ANOS_CHOICES = [(year, str(year)) for year in range(2020, datetime.date.today().year + 5)] # Exemplo de 2020 até 5 anos no futuro
    ano = forms.ChoiceField(choices=ANOS_CHOICES, widget=forms.Select(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}))

    class Meta:
        model = Competencia
        fields = ['mes', 'ano', 'ativa', 'total_pago', 'observacoes']
        widgets = {
            'mes': forms.Select(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'total_pago': forms.NumberInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'border-color: #ced4da; box-shadow: none;'}),
        }



# ... seus outros formulários ...

class SubvaloresForm(forms.ModelForm):
    class Meta:
        model = Subvalores
        fields = ['nome', 'valor', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'style': 'border-color: #ced4da; box-shadow: none;'}),
        }

class PagarContaComSubvaloresForm(forms.ModelForm):
    class Meta:
        model = ContaPaga
        fields = ['data_pagamento', 'valor_pago', 'comprovante', 'observacoes']
        widgets = {
            'data_pagamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'valor_pago': forms.NumberInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'comprovante': forms.FileInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'border-color: #ced4da; box-shadow: none;'}),
        }

    def __init__(self, *args, **kwargs):
        self.conta = kwargs.pop('conta', None)
        self.competencia = kwargs.pop('competencia', None)
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Remove o ":" padrão das labels
        
        # Definir valores iniciais se conta e competência forem fornecidos
        if self.instance and not self.instance.pk and self.conta and self.competencia:
            self.instance.conta = self.conta
            self.instance.competencia = self.competencia

# Criar um formset para os subvalores com no máximo 10 formulários
SubvaloresFormSet = inlineformset_factory(
    Conta,
    Subvalores,
    form=SubvaloresForm,
    extra=1,
    max_num=20,
    can_delete=True,
    validate_max=True
)
