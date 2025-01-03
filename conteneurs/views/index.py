from django.shortcuts import render
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.views import View
from conteneurs.models import *  # Assurez-vous que le modèle Dossier est correctement importé
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from datetime import timedelta
from django.views.generic import TemplateView
def index(request):
    # Message de bienvenue avec le nom d'utilisateur
    messages.add_message(request, messages.SUCCESS, "Bienvenue %s" % request.user.username)

    # Filtrer les utilisateurs en ligne
    users_online = Personnel.objects.filter(is_online=True)

    # Nombre d'utilisateurs en ligne
    num_connected_users = users_online.count()

    # Nombre de dossiers avec le statut "sélection en cours"
    selection_en_cours = Dossier.objects.filter(statut="selection_en_cours").count()


    # Grouper les conteneurs par mois et compter combien ont été utilisés par mois
    conteneurs_par_mois = Conteneur.objects.annotate(month=TruncMonth('Date_ajout')).values('month').annotate(total=Count('id')).order_by('month')

    # Nombre de dossiers avec le statut "terminé" au cours du mois actuel
    current_month = timezone.now().month
    current_year = timezone.now().year
    dossiers_termine_mois = Dossier.objects.filter(statut="dossier_termine", Date_ajout__month=current_month, Date_ajout__year=current_year).count()

    dossiers_attente_mois = Dossier.objects.filter(statut="en_attente", Date_ajout__month=current_month, Date_ajout__year=current_year).count()

    # Nombre de dossiers avec le statut "terminé" au cours de l'année actuelle
    dossiers_termine_annee = Dossier.objects.filter(statut="dossier_termine", Date_ajout__year=current_year).count()

    # Nombre de conteneurs ajoutés au cours de l'année actuelle
    conteneurs_annee = Conteneur.objects.filter(Date_ajout__year=current_year).count()
    
      # Obtenir la date actuelle
    current_date = timezone.now()
    
    # Nombre de dossiers  du mois actuel
    current_month = timezone.now().month
    current_year = timezone.now().year
    dossiers_mois = Dossier.objects.filter( Date_ajout__month=current_month, Date_ajout__year=current_year).count()
    
    dossiers_aconage_mois = Dossier.objects.filter(statut="aconage_en_cours", Date_ajout__month=current_month, Date_ajout__year=current_year).count()

    # Préparer les données pour Morris.js
    data = []
    for item in conteneurs_par_mois:
        data.append({
            'month': item['month'].strftime('%Y-%m'),
            'count': item['total']
        })
        
    

    # Passer les informations au template
    context = {
        'num_connected_users': num_connected_users,
        'selection_en_cours': selection_en_cours,
        'conteneur_data': data,
        'conteneurs_annee':conteneurs_annee,
        'dossiers_termine_annee':dossiers_termine_annee,
        'dossiers_termine_mois':dossiers_termine_mois,
        'current_date': current_date ,
        'dossiers_mois':dossiers_mois,
        'dossiers_attente_mois': dossiers_attente_mois,
        'dossiers_aconage_mois':dossiers_aconage_mois # Ajouté pour les graphiques de dossiers par mois et par année
    }

    return render(request, "index.html", context)

class DossierStatsDataView(View):
    def get(self, request, *args, **kwargs):
            # Obtenir les statistiques des 12 derniers mois
            current_date = timezone.now()
            start_date = current_date - timedelta(days=365)
            
            # Requête pour tous les dossiers par mois
            total_dossiers = (
                Dossier.objects
                .filter(date_creation__gte=start_date)
                .annotate(month=TruncMonth('date_creation'))
                .values('month')
                .annotate(total_dossiers=Count('id'))
                .order_by('month')
            )
            
            # Requête pour les dossiers terminés par mois
            dossiers_termines = (
                Dossier.objects
                .filter(
                    date_creation__gte=start_date,
                    statut='dossier_termine'
                )
                .annotate(month=TruncMonth('date_creation'))
                .values('month')
                .annotate(dossiers_termines=Count('id'))
                .order_by('month')
            )
            
            # Créer un dictionnaire pour combiner les résultats
            stats_by_month = {}
            
            # Ajouter les totaux
            for entry in total_dossiers:
                month_str = entry['month'].strftime('%B %Y')
                stats_by_month[month_str] = {
                    'month': month_str,
                    'total_dossiers': entry['total_dossiers'],
                    'dossiers_termines': 0
                }
            
            # Ajouter les dossiers terminés
            for entry in dossiers_termines:
                month_str = entry['month'].strftime('%B %Y')
                if month_str in stats_by_month:
                    stats_by_month[month_str]['dossiers_termines'] = entry['dossiers_termines']
            
            # Convertir en liste pour l'API
            stats_list = list(stats_by_month.values())
            
            return JsonResponse(stats_list, safe=False)