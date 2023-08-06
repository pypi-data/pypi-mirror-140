from django.shortcuts import render
from .models import *
from employee.models import *


def load_posts(request):
	mun_id = request.GET.get('municipality')
	posts = AdministrativePost.objects.filter(municipality_id=mun_id).order_by('name')
	return render(request, 'custom/posts_dropdown.html', {'posts': posts})

def load_villages(request):
	post_id = request.GET.get('post')
	villages = Village.objects.filter(administrativepost_id=post_id).order_by('name')
	return render(request, 'custom/villages_dropdown.html', {'villages': villages})

def load_aldeia(request):
	post_id = request.GET.get('post')
	aldeia = Aldeia.objects.filter(village_id=post_id).order_by('name')
	print(aldeia)
	return render(request, 'custom/aldeia_dropdown.html', {'aldeia': aldeia})
