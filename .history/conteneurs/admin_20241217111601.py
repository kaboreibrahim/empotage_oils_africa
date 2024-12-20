from django.contrib import admin
from .models import *

# Inline pour les conteneurs
class ConteneurInline(admin.TabularInline):  # Vous pouvez aussi utiliser admin.StackedInline pour un affichage en blocs
    model = Conteneur
    extra = 1  # Nombre de conteneurs supplémentaires à afficher

 
# Configuration pour le modèle Dossier
@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ('date_creation', 'statut', 'projet','TRD', 'client', 'agent_selection', 'agent_acconage','port_de_chargement', 'port_de_dechargement','compagnie_maritime', 'site', 'commodite', 'secretaire')
    search_fields = ('projet', 'statut', 'Personnel_type', 'client__nom')
    list_filter = ('statut', 'projet', 'date_creation', 'secretaire')
    date_hierarchy = 'date_creation'
    inlines = [ConteneurInline]  # Ajout de l'inline pour les conteneurs

# Autres configurations d'administration (comme avant)
@admin.register(Personnel)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'Personnel_type')
    search_fields = ('username', 'first_name', 'last_name', 'Personnel_type')
    list_filter = ('Personnel_type',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse', 'contact', 'email')
    search_fields = ('nom', 'adresse')

@admin.register(Commodite)
class CommoditeAdmin(admin.ModelAdmin):
    list_display = ('nom_commodite',)
    search_fields = ('nom_commodite',)

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('nom_site',)
    search_fields = ('nom_site',)

@admin.register(Pays)
class  PaysAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)


@admin.register(Site_empotage)
class Site_empotageAdmin(admin.ModelAdmin):
    list_display = ('nom_site',)
    search_fields = ('nom_site',)
@admin.register(POD)
class PortDeDechargementAdmin(admin.ModelAdmin):
    list_display = ('nom_POD',)
    search_fields = ('nom_POD',)

@admin.register(POL)
class PortDeChargementAdmin(admin.ModelAdmin):
    list_display = ('nom_POL','Date_ajout')
    search_fields = ('nom_POL',)

@admin.register(CompagnieMaritime)
class CompagnieMaritimeAdmin(admin.ModelAdmin):
    list_display = ('nom_compagnie_maritime',)
    search_fields = ('nom_compagnie_maritime',)

@admin.register(Conteneur)
class ConteneurAdmin(admin.ModelAdmin):
    list_display = ('reference', 'etat', 'dossier', 'agent_selection', 'agent_acconage','Date_ajout')
    list_filter = ('dossier', 'etat')
    search_fields = ('reference', 'dossier__projet')

    def save_model(self, request, obj, form, change):
        if not change and not obj.agent_acconage:
            obj.agent_selection = request.Personnel_type
        elif change and 'agent_acconage' in form.changed_data:
            obj.agent_acconage = request.Personnel_type
        super().save_model(request, obj, form, change)


 
 
@admin.register(FichierJoint)
class FicherJointAdmin(admin.ModelAdmin):
    
    pass




from django.contrib import admin
from .models import Dossier2, Document_Facture, AutreDocument, Images

class DocumentFactureInline(admin.TabularInline):
    model = Document_Facture
    extra = 1
    readonly_fields = ('Date_ajout',)

class AutreDocumentInline(admin.TabularInline):
    model = AutreDocument
    extra = 1
    readonly_fields = ('Date_ajout',)

class ImagesInline(admin.TabularInline):
    model = Images
    extra = 1
    readonly_fields = ('Date_ajout',)

@admin.register(Dossier2)
class Dossier2Admin(admin.ModelAdmin):
    list_display = ('projet', 'TRD', 'client', 'Date_ajout','date_creation')
    search_fields = ('projet', 'TRD')
    list_filter = ('client',)
    inlines = [DocumentFactureInline, AutreDocumentInline, ImagesInline]
