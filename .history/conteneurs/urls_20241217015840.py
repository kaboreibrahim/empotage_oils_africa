from django.urls import path
#from django.contrib.auth import view
#from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView,PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import views as auth_views
from conteneurs.views import *
from conteneurs.views.compagnie_maritime import *
from conteneurs.views.site import *
from conteneurs.views.client import *
from conteneurs.views.dossiers import *
from conteneurs.views.dossier_selection import DossierSelectionListView
from django.views.generic import RedirectView
urlpatterns=[
        path('', RedirectView.as_view(url='login/', permanent=False)),
        path('Accueil/', index, name='index'),
        
        ### view de connexion
        path('register/', register, name='register'),
        path('login/', user_login, name='login'),
        path('deconnexion',deconnection,name='deconnexion'),
        path('verify/', verify, name='verify'),
        
          #view de recuperation de compte 
        path('reset-password/', CustomPasswordResetView.as_view(), name='password_reset'),
        path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/rest/password_reset_done.html'), name='password_reset_done'),
        path('reset-password/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/rest/password_reset_confirm.html'), name='password_reset_confirm'),
        path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/rest/password_reset_complete.html'), name='password_reset_complete'),
        
        # view pour POL
        path('POL/list/',POLView.as_view(),name='pol_list'),
        path('POL/create/',POLCreateView.as_view(),name='pol_create'),
        path('Pol/edit/<uuid:pk>/', POLUpdateView.as_view(), name='pol_edit'),
        path('Pol/delete/<uuid:pk>/', POLDeleteView.as_view(), name='pol_delete'),
        
        
         # view pour POD
        path('POD/list/',PODView.as_view(),name='pod_list'),
        path('POD/create/',PODCreateView.as_view(),name='pod_create'),
        path('POD/edit/<uuid:pk>/', PODUpdateView.as_view(), name='pod_edit'),
        path('POD/delete/<uuid:pk>/', PODDeleteView.as_view(), name='pod_delete'),
        
        
         
        # view pour Compagnie maritime
        path('Compagnie/Maritime/list/',CompagnieMaritimeView.as_view(),name='CompagnieMaritime_list'),
        path('Compagnie/Maritime/create/',CompagnieMaritimeCreateView.as_view(),name='CompagnieMaritime_create'),
        path('Compagnie/Maritime/edit/<uuid:pk>/', CompagnieMaritimeUpdateView.as_view(), name='CompagnieMaritime_edit'),
        path('Compagnie/Maritime/delete/<uuid:pk>/', CompagnieMaritimeDeleteView.as_view(), name='CompagnieMaritime_delete'),
        
        
        # view pour les commodies
        path('Commodite/list/',CommoditeView.as_view(),name='Commodite_list'),
        path('Commodite/create/',CommoditeCreateView.as_view(),name='Commodite_create'),
        path('Commodite/edit/<uuid:pk>/',CommoditeUpdateView.as_view(), name='Commodite_edit'),
        path('Commodite/delete/<uuid:pk>/', CommoditeDeleteView.as_view(), name='Commodite_delete'),
        
        
            # view pour les Sites
        path('Site/list/',SiteView.as_view(),name='Site_list'),
        path('Site/create/',SiteCreateView.as_view(),name='Site_create'),
        path('Site/edit/<uuid:pk>/',SiteUpdateView.as_view(), name='Site_edit'),
        path('Site/delete/<uuid:pk>/', SiteDeleteView.as_view(), name='Site_delete'),
        
            # view pour les Sites empotage
        path('Site/empoatge/list/',Site_empotageView.as_view(),name='Site_empotage_list'),
        path('Site/empotage/create/',Site_empotageCreateView.as_view(),name='Site_empotage_create'),
        path('Site/empotage/edit/<uuid:pk>/',Site_empotage_empotageUpdateView.as_view(), name='Site_empotage_edit'),
        path('Site/empotage/delete/<uuid:pk>/', Site_empotageDeleteView.as_view(), name='Site_empotage_delete'),
        
            # view pour les client
        path('Client/list/',ClientView.as_view(),name='Client_list'),
        path('Client/create/',ClientCreateView.as_view(),name='Client_create'),
        path('Client/edit/<uuid:pk>/',ClientUpdateView.as_view(), name='Client_edit'),
        path('Client/delete/<uuid:pk>/', ClientDeleteView.as_view(), name='Client_delete'),
        
              # view pour les dossier
        path('Dossier/list/',DossierView.as_view(),name='Dossier_list'),
        path('Dossier/create/',DossierCreateView.as_view(),name='Dossier_create'),
        path('Dossier/edit/<uuid:pk>/',DossierUpdateView.as_view(), name='Dossier_edit'),
        path('Dossier/delete/<uuid:pk>/', DossierDeleteView.as_view(), name='Dossier_delete'),
        path('dossier/<uuid:pk>/detail/', dossier_detail, name='dossier_detail'),
        path('dossier/<uuid:pk>/detail/gabon', dossier_detail_gabon, name='dossier_detail_gabon'),
        
            #view pour  la creation de dossier de gabon
        path('Dossier/list/gabon',DossierViewGabon.as_view(),name='Dossier_list_gabon'),
        path('dossier/gabon/create/', DossierCreateGabonView.as_view(), name='dossier_gabon_create'),
        path('dossier/gabon/edit/<uuid:pk>/', DossierUpdateGabonView.as_view(), name='dossier_gabon_edit'),
        path('dossier/gabon/delete/<uuid:pk>/', DossierDeleteGabonView.as_view(), name='dossier_gabon_delete'),
        # path('dossier/gabon/<uuid:pk>/detail/', dossier_gabon_detail, name='dossier_gabon_detail'),
        
       

         # view pour les dossierselection
        path('dossiers/selection/conteneur/', DossierSelectionListView.as_view(), name='dossier_list_selction'),
        path('dossier/<uuid:dossier_id>/conteneurs/', view_conteneurs, name='view_conteneurs'),
        path('dossier/<uuid:dossier_id>/conteneurs/iso', view_iso, name='view_iso'),
        path('dossier/<uuid:dossier_id>/conteneurs/ajouter/', manage_conteneurs, name='manage_conteneurs'),
        path('dossier/<uuid:dossier_id>/isotanks/ajouter/', manage_conteneursIso, name='manage_conteneursIso'),
        path('dossier/<uuid:dossier_id>/soumettre/', soumettre_dossier, name='soumettre_dossier'),
        path('conteneur/<uuid:pk>/edit/', ConteneurUpdateView.as_view(), name='modifier_conteneur'),
        path('conteneur/<uuid:pk>/delete/', ConteneurDeleteView.as_view(), name='supprimer_conteneur'),
        
        path('iso/<uuid:pk>/edit/', IsoUpdateView.as_view(), name='modifier_iso'),        
        path('iso/<uuid:pk>/delete/', IsoDeleteView.as_view(), name='supprimer_conteneur_iso'),
        
        path('dossier/<uuid:dossier_id>/pdf/',generate_dossier_pdf, name='generate_dossier_pdf'),
        path('dossier/menu/sous/dossier/<uuid:pk>', menu_sous_dossier, name='menu_sous_dossier'),
        path('dossier/menu/sous/dossier/facture/<uuid:pk>', facture_list, name='facture_list'),
        path('dossier/menu/sous/dossier/autre/dossier/<uuid:pk>', autre_dossier_list, name='autre_dossier_list'),
        path('dossier/menu/sous/dossier/autre/dossier/<uuid:pk>/ajouter/', autre_dossier_create, name='autre_dossier_create'),
        path('dossier/menu/sous/dossier/image/<uuid:pk>/', images_list, name='images_list'),
        path('dossier/menu/sous/dossier/facture/<uuid:pk>/ajouter/',facture_create, name='creer_facture'),
        path('dossier/menu/sous/dossier/image/<uuid:pk>/ajouter/',images_create,name='images_create'),
        path('Dossier/list/archive',DossierView2.as_view(),name='Dossier_list2'),
        path('Dossier/create/archive',DossierCreateView2.as_view(),name='Dossier_create2'),
        path('Dossier/edit/<uuid:pk>/archive',DossierUpdateView2.as_view(), name='Dossier_edit2'),
        # view de personne
        path('agent/list/', PersonnelView.as_view(), name='Personnel_list'),
        
        #view pour les dossieracconage
        
        path('dossier/acconage/list/', DossierAccoangeListView.as_view(), name='dossier_list_Accoange'),
        path('dossier/<uuid:dossier_id>/acconage/<uuid:conteneur_id>/', manage_conteneurs_acconage, name='manage_conteneurs_acconage'),  
        path('conteneur/<uuid:conteneur_id>/', afficher_detail_conteneur, name='detail_conteneur'),
        path('conteneur/<uuid:conteneur_id>/dossier/<uuid:dossier_id>/modifier/',modifier_conteneur, name='modifier_conteneur_aconer'),
        path('dossier/<uuid:dossier_id>/pdf/aconage/',generate_dossier_aconage_pdf, name='generate_dossier_aconage_pdf'),
        path('dossier/<uuid:dossier_id>/soumettre/aconage/', soumettre_dossier_acconage, name='soumettre_dossier_acconage'),
        path('dossier/retrouver/<uuid:dossier_id>/', retrograder_dossier, name='retrograder_dossier'),
        path('api/dossier-stats/', DossierStatsDataView.as_view(), name='dossier_stats'),
        

        
]
        
        

        
        
        
        

    



