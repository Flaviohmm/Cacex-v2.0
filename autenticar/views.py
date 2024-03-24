from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib import auth
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from .forms import PasswordResetRequestForm, CustomSetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse
from .models import CustomUser
from django.contrib.auth.tokens import default_token_generator
from django.views import View


def cadastro(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        # Altere esta condição para verificar o comprimento da senha
        if len(username.strip()) == 0 or len(senha.strip()) == 0:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/auth/cadastro')
        
        user = CustomUser.objects.filter(username=username)

        if user.exists():
            messages.add_message(request, constants.ERROR, 'Já existe um usuário com esse nome cadastrado')
            return redirect('/auth/cadastro')
        
        try:
            user = CustomUser.objects.create_user(username=username, password=senha)
            user.save()
            messages.add_message(request, constants.SUCCESS, 'Cadastro realizado com sucesso')
            return redirect('/auth/login')
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            return redirect('/auth/cadastro')
        

def login(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        usuario = auth.authenticate(request, username=username, password=senha)

        if not usuario:
            messages.add_message(request, constants.ERROR, 'Usuario ou senha inválidos')
            return redirect('/auth/login')
        else:
            if usuario.is_logged_in:
                messages.add_message(request, constants.ERROR, 'Este usuário já está logado')
                return redirect('/auth/login')
            else:
                usuario.is_logged_in = True
                usuario.save()
                auth_login(request, usuario)
                return redirect('/')
        

def sair(request):
    if request.user.is_authenticated:
        user = request.user
        user.is_logged_in = False
        user.save()
        auth.logout(request)
    return redirect('/auth/login')


User = get_user_model()


class PasswordResetRequestView(View):
    template_name = 'password_reset_request.html'

    def get(self, request):
        form = PasswordResetRequestForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                messages.add_message(request, constants.ERROR, 'Usuário não encontrado.')
                return redirect('/auth/password_reset_request')

            # Gera ou recupera um token único para o usuário
            token = user.reset_password_token
            if not token:
                token = default_token_generator.make_token(user)
                user.reset_password_token = token
                user.save()

            # Gera a URL de redefinição de senha
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})

            # Redireciona para a página de redefinição de senha
            messages.add_message(request, constants.SUCCESS, 'Token de redefinição de senha gerado com sucesso. Envie este token ao usuário.')
            return redirect(reset_url)

        return render(request, self.template_name, {'form': form})


class PasswordResetConfirmView(View):
    template_name = 'password_reset_confirm.html'

    def get(self, request, uidb64, token):
        try:
            uid = force_bytes(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = CustomSetPasswordForm(user)
            return render(request, self.template_name, {'form': form, 'uidb64': uidb64, 'token': token})
        else:
            messages.add_message(request, constants.ERROR, 'O link de redefinição de senha é inválido ou expirou.')
            return redirect('/auth/password_reset_request')

    def post(self, request, uidb64, token):
        try:
            uid = force_bytes(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request, constants.SUCCESS, 'Senha alterada com sucesso. Faça login com a nova senha.')
                return redirect('/auth/login')
            else:
                return render(request, self.template_name, {'form': form, 'uidb64': uidb64, 'token': token})

        messages.add_message(request, constants.ERROR, 'O link de redefinição de senha é inválido ou expirou.')
        return redirect('/auth/password_reset_request')