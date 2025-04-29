from django import forms
from .models import Conta, ContaEmbutida
from django.core.validators import MinValueValidator, MaxValueValidator

class ContaForm(forms.ModelForm):
    data_vencimento = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
        label="Dia de Vencimento"
    )

    class Meta:
        model = Conta
        fields = ['nome', 'data_vencimento', 'observacoes', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'border-color: #ced4da; box-shadow: none;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Remove o ":" padrão das labels
        self.fields['ativa'].label = "Conta Ativa" # Define o label do checkbox

class ContaEmbutidaForm(forms.ModelForm):
    data_vencimento = forms.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
        label="Dia de Vencimento"
    )
    
    class Meta:
        model = ContaEmbutida
        fields = ['nome', 'data_vencimento', 'observacoes', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'style': 'border-color: #ced4da; box-shadow: none;'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'border-color: #ced4da; box-shadow: none;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # Remove o ":" padrão das labels
        self.fields['ativa'].label = "Conta Ativa" # Define o label do checkbox
