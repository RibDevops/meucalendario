from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendario_view, name='calendario'),
    path('evento/criar/', views.evento_criar, name='evento_criar'),
    path('evento/<int:pk>/', views.evento_detalhes, name='evento_detalhes'),
    path('evento/<int:pk>/editar/', views.evento_editar, name='evento_editar'),
    path('evento/<int:pk>/excluir/', views.evento_excluir, name='evento_excluir'),
    path('eventos/json/', views.eventos_json, name='eventos_json'),
    path('evento/quick-add/', views.evento_quick_add, name='evento_quick_add'),
]
