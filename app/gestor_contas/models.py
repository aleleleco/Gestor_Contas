from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Competencia(models.Model):
    mes = models.IntegerField()
    ano = models.IntegerField()
    aberta = models.BooleanField(default=True)
    total_pago = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    data_abertura = models.DateField(auto_now_add=True)
    data_fechamento = models.DateField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('mes', 'ano')  # Garante que não haja duplicidade de mês/ano

    def __str__(self):
        return f'{self.mes}/{self.ano}'

class Conta(models.Model):
    nome = models.CharField(max_length=255)
    data_vencimento = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name="Dia de Vencimento"  # Opcional: Um nome mais amigável para o campo
    )
    observacoes = models.TextField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class ContaEmbutida(models.Model):
    nome = models.CharField(max_length=255)
    
    data_vencimento = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name="Dia de Vencimento"  # Opcional: Um nome mais amigável para o campo
    )

    observacoes = models.TextField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativa = models.BooleanField(default=True)


    def __str__(self):
        return self.nome

class ItemContaEmbutida(models.Model):
    conta_embutida = models.ForeignKey(ContaEmbutida, on_delete=models.CASCADE, related_name='itens')
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_compra = models.DateField(null=True, blank=True)
    parcelado = models.BooleanField(default=False)
    numero_parcela = models.IntegerField(null=True, blank=True)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return self.descricao

class ContaEsporadica(models.Model):
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_gasto = models.DateField()
    observacoes = models.TextField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.descricao

class ContaPaga(models.Model):
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE, related_name='pagamentos')
    data_pagamento = models.DateField()
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    comprovante = models.FileField(upload_to='comprovantes/', null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    data_registro = models.DateTimeField(auto_now_add=True)
    # Adicionando campos para referenciar os diferentes tipos de contas pagas
    conta = models.ForeignKey(Conta, on_delete=models.SET_NULL, null=True, blank=True)
    conta_embutida = models.ForeignKey(ContaEmbutida, on_delete=models.SET_NULL, null=True, blank=True)
    conta_esporadica = models.ForeignKey(ContaEsporadica, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Pagamento de R$ {self.valor_pago} em {self.data_pagamento} na competência {self.competencia}'
    

class Submenu(models.Model):
    nome = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    icone = models.CharField(max_length=50)
    pagina = models.CharField(max_length=100)

    def __str__(self):
        return self.nome