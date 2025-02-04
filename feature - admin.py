from django.contrib import admin
from dbmanager import models
from dbmanager import views
from django.contrib.admin import FieldListFilter

# Register your models here.

@admin.register(models.MeusBancos)
class MeusBancos(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.groups.filter(name__in=['backup', 'Teste', 'desenvolvimento']).exists():
            return qs
        return qs.filter(owner=request.user)

    def has_delete_permission(self, request, obj=None):
        """
        - Superusuários e o grupo 'backup' podem deletar qualquer banco.
        - Usuários dos grupos 'Teste' e 'desenvolvimento' NÃO podem deletar nenhum banco, nem os próprios, isso garante que o controle fique mais
        centralizado para o responsável por manter a organização do servidores (normalmente a pessoa que cuida dos backups).
        """
        if request.user.is_superuser or request.user.groups.filter(name='backup').exists():
            return True
        return False  # Bloqueia a exclusão para todos os usuários que não sejam superusuário ou do grupo 'backup'

    def has_add_permission(self, request):
        return True  # Todos podem adicionar bancos

    def has_change_permission(self, request, obj=None):
        if obj:
            if request.user.groups.filter(name__in=['Teste', 'desenvolvimento']).exists():
                return obj.owner == request.user  # Só pode modificar seus próprios registros
        return True  

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name='backup').exists():
            return [
                (None, {'fields': ('owner', 'servidor', 'nmbanco', 'estouusando')}),
            ]
        return [
            (None, {'fields': ('servidor', 'nmbanco',)}),
            ('Configuração do Usuário', {'fields': ('estouusando',)})
        ]

    list_display = ('owner', 'servidor', 'nmbanco', 'estouusando', 'dtcriacao')
    list_filter = ('owner', 'estouusando', 'dtcriacao', 'servidor')
    search_fields = ('nmbanco',)
    ordering = ('dtcriacao',)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name='backup').exists():
            return ()  

        if obj:
            if request.user.groups.filter(name__in=['Teste', 'desenvolvimento']).exists():
                if obj.owner != request.user:
                    return ('owner', 'servidor', 'nmbanco', 'estouusando')
            return ('owner',)

        return ()  

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not request.user.groups.filter(name='backup').exists():
            obj.owner = request.user  

        if change:  
            original_obj = models.MeusBancos.objects.get(pk=obj.pk)
            if request.user.groups.filter(name__in=['Teste', 'desenvolvimento']).exists():
                if original_obj.owner != request.user:
                    self.message_user(request, "Você não pode modificar registros de outros usuários.", level='error')
                    return  

        super().save_model(request, obj, form, change)

@admin.register(models.Servidores)
class Servidores(admin.ModelAdmin):
    list_display = ('nmservidor', 'ipservidor', 'sistemaoperacional', 'dtcriacao')
    ordering = ('dtcriacao',)
