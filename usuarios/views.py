from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django_ratelimit.decorators import ratelimit

# LEMBRE QUE VC CONFIGUROU O MIDDLEWARE NO SETTINGS.PY COM 'django_ratelimit.middleware.RatelimitMiddleware' ELE TEM QUE SER O PRIMEIRO PARA DAR CERTO.

@ratelimit(key='ip', rate='5/d')  # block=False by default
def login_view(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        messages.error(request, 'Você excedeu o limite de tentativas de login. Por favor, tente novamente mais tarde.')
        return render(request, 'registration/login.html', {'error': messages.get_messages(request)})
        
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Email ou senha incorretos')
    return render(request, 'registration/login.html', {'error': messages.get_messages(request)})

@login_required(login_url='/login/')
def index(request):
    return render(request, 'index.html')
