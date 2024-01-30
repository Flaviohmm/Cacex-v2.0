from django.shortcuts import render


def base_admin(request):
    return render(request, 'base_admin.html')
