from django.urls import path
from . import views
app_name = 'custom'
urlpatterns = [
	path('ajax/load-posts/', views.load_posts, name='ajax_load_posts'),
	path('ajax/load-villages/', views.load_villages, name='ajax_load_villages'),
	path('ajax/load-aldeia/', views.load_aldeia, name='ajax_load_aldeia'),
]

