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
        if request.user.groups.filter(name='backup').exists():
            return qs
        return qs.filter(owner=request.user)

    def get_fieldsets(self, request, obj=None):
        #if request.user.is_superuser:
        if request.user.groups.filter(name='backup').exists():
            return [
                (None, {'fields': ('owner', 'servidor', 'nmbanco', 'estouusando')}),
            ]
        else:
            return [
                (None, {'fields': ('servidor', 'nmbanco', 'estouusando')}),
            ]
    
    #fields = ['servidor', 'nmbanco', 'estouusando',] 
    list_display = 'owner', 'servidor', 'nmbanco','estouusando', 'dtcriacao',
    list_filter = ('owner', 'estouusando', 'dtcriacao', 'servidor',)
    list_editable = 'estouusando',
    search_fields = ('nmbanco',)
    ordering = 'dtcriacao',

    def save_model(self, request, obj, form, change):
        if not request.user.groups.filter(name='backup').exists():
            obj.owner = request.user
        super().save_model(request, obj, form, change)
        

@admin.register(models.Servidores)
class Servidores(admin.ModelAdmin):
    list_display = 'nmservidor', 'ipservidor', 'sistemaoperacional', 'dtcriacao',
    ordering = 'dtcriacao',