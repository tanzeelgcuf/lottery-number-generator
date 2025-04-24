from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('import/', views.import_data, name='import_data'),
    path('generate/', views.generate_numbers, name='generate_numbers'),
    path('results/', views.lottery_results, name='lottery_results'),
    path('api/generate/', views.api_generate_numbers, name='api_generate_numbers'),
]