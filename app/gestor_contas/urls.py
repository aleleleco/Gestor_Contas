from django.urls import path
from app.gestor_contas import views
from django.conf import settings
from django.conf.urls.static import static



app_name = 'gestor_contas'

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro_conta/', views.cadastro_conta, name='cadastro_conta'),
    path('cadastro_contas/', views.cadastro_contas, name='cadastro_contas'),
    # path('cadastro_contas_embutidas/', views.cadastro_contas_embutidas, name='cadastro_contas_embutidas'),
    path('cadastro_competencia/', views.cadastro_competencia, name='cadastro_competencia'),
    path('altera_status/<int:id>/', views.altera_status, name='altera_status'),
    path('administracao/', views.administracao, name='administracao'),
    path('contasadmin/', views.contasadmin, name='contasadmin'),
    path('competenciaadm/', views.competenciaadm, name='competenciaadm'),
    path('pagamentos/', views.pagamentos, name='pagamentos'),
    path('contas_mensais/<int:id>', views.contas_mensais, name='contas_mensais'),
    path('pagar_conta/<int:conta_id>/<int:competencia_id>/', views.pagar_conta, name='pagar_conta'),
    path('pagar_conta_subvalor/<int:conta_id>/<int:competencia_id>/', views.pagar_conta_subvalor, name='pagar_conta_subvalor'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorio_meses/', views.relatorio_meses, name='relatorio_meses'),
    path('editar_conta_pagar/<int:conta_id>/<int:competencia_id>', views.editar_conta_pagar, name='editar_conta_pagar'),

    
    
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)