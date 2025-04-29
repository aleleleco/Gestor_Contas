from django.urls import path
from app.gestor_contas import views

app_name = 'gestor_contas'

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro_conta/', views.cadastro_conta, name='cadastro_conta'),
    path('cadastro_contas/', views.cadastro_contas, name='cadastro_contas'),
    path('cadastro_contas_embutidas/', views.cadastro_contas_embutidas, name='cadastro_contas_embutidas'),
    path('cadastro_competencia/', views.cadastro_competencia, name='cadastro_competencia'),
    path('altera_status/<int:id>/', views.altera_status, name='altera_status'),
    
    ]