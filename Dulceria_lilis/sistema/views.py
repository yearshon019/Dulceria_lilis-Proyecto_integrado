from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
@login_required
def dashboard(request):
    visitas = request.session.get('visitas', 0)
    request.session['visitas'] = visitas + 1
    return render(request, 'dashboard.html', {'visitas': visitas})

