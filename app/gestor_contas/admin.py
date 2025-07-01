from django.contrib import admin
from .models import Conta, Competencia, ContaPaga, Subvalores, Parcelamento, Tags, GastosGerais, Pessoa, TipoPagamento

# Register your models here.


admin.site.register(Conta)
admin.site.register(Competencia)
admin.site.register(ContaPaga)
admin.site.register(Subvalores)
admin.site.register(Parcelamento)
admin.site.register(Pessoa)
admin.site.register(TipoPagamento)

class ListandoTags(admin.ModelAdmin):
    list_display = ('nome',)
    list_display_links = ('nome',)
    search_fields = ('nome',)
    list_per_page = 10

admin.site.register(Tags, ListandoTags)

class ListandoGastosGerais(admin.ModelAdmin):
    list_display = ('nome', 'valor', 'competencia', 'contabiliza', 'data_compra', 'pessoa', 'tipo_pagamento')
    list_display_links = ('nome',)
    search_fields = ('nome',)
    list_per_page = 10

admin.site.register(GastosGerais, ListandoGastosGerais)

