from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.db.models import Q
from django.http import FileResponse, HttpResponse
from .models import MeusBancos

def baixar_backup_manager(request):
    caminho_arquivo = r"\\server01\Empresa\Versoes\APLICATIVOS_DE_APOIO\BackupManager\BackupManager 01.00.02-00\BackupManager 01.00.02-00.exe"
    try:
        return FileResponse(open(caminho_arquivo, 'rb'), as_attachment=True, filename='BackupManager.exe')
    except FileNotFoundError:
        return HttpResponse("Erro: Arquivo não encontrado no server 01.")
    except Exception as e:
        return HttpResponse(f"Erro ao processar o download: {e}")

class BancosSemUso(ListView):
    model = MeusBancos
    context_object_name = 'bancossemuso'
    template_name = 'bancossemuso.html'
    paginate_by = 10

    def get_queryset(self):
        bancoemuso = MeusBancos.objects.using('default').filter(estouusando=True)
        query_name = self.request.GET.get('query', '')
        if query_name:
            object_list = MeusBancos.objects.using('default').order_by('-dtcriacao').filter(
                (Q(nmbanco__icontains=query_name) |
                 Q(owner__username__icontains=query_name) |
                 Q(servidor__ipservidor__icontains=query_name) |
                 Q(dtcriacao__icontains=query_name)),
                Q(estouusando=False)
            ).exclude(nmbanco__in=list(bancoemuso))
            return object_list
        else:
            return MeusBancos.objects.using('default').order_by('-dtcriacao').filter(estouusando=False).exclude(nmbanco__in=list(bancoemuso))

class BancosEmUso(ListView):
    model = MeusBancos
    context_object_name = 'bancosemuso'
    template_name = 'bancosemuso.html'

    def get_queryset(self):
        query_name = self.request.GET.get('query', '')
        if query_name:
            object_list = MeusBancos.objects.using('default').order_by('-dtcriacao').filter(
                (Q(nmbanco__icontains=query_name) |
                 Q(owner__username__icontains=query_name) |
                 Q(servidor__ipservidor__icontains=query_name) |
                 Q(dtcriacao__icontains=query_name)),
                Q(estouusando=True)
            )
            return object_list
        else:
            return MeusBancos.objects.using('default').order_by('-dtcriacao').filter(estouusando=True)

class Home(TemplateView):
    template_name = 'home.html'
