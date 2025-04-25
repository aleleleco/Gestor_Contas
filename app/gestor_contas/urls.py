from django.urls import path
from app.gestor_contas import views

app_name = 'gestor_contas'

urlpatterns = [
    path('', views.index, name='index'),]