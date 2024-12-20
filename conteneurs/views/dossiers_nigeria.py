from django.http import HttpRequest, HttpResponseRedirect
from django.views.generic import ListView, CreateView,UpdateView,DeleteView,DetailView
from conteneurs.models import *
from conteneurs.forms import *
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404,render
from django.core.paginator import Paginator
from braces.views import FormMessagesMixin
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.core.mail import EmailMessage

from django.db.models import Q

@method_decorator(login_required, name='dispatch')
class DossierViewNigeria(ListView):
    model = Dossier
    context_object_name = 'Dossier_list'
    template_name = 'pages/Dossier/Dossier_list_Nigeria.html'

    def get_queryset(self):
        queryset = Dossier.objects.all()
        pays = Pays.objects.filter(nom='Nigeria').first()  # Récupérer l'objet Pays pour 'Nigeria'
        if pays:
            queryset = queryset.filter(pays=pays)

        statut = self.request.GET.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(projet__icontains=search_query) | 
                Q(TRD__icontains=search_query) |
                Q(booking__icontains=search_query)
            )
        return queryset.order_by('-Date_ajout')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nombre_dossiers'] = self.get_queryset().count()  # Nombre de dossiers
        return context
    

@method_decorator(login_required, name='dispatch')
class DossierCreateNigeriaView(CreateView):
    model = Dossier
    form_class = DossiersNigeriaForm
    template_name = "pages/Dossier/Dossier_create_Nigeria.html"
    success_url = reverse_lazy('Dossier_list_Nigeria')
    form_invalid_message = "Oups, quelque chose s'est mal passé!"

    def get_form_valid_message(self):
        return f"{self.object} créé avec succès!"
    
    def form_valid(self, form):
        # Assigner la secrétaire connectée (utilisateur actuel)
        dossier = form.save(commit=False)
        dossier.secretaire = self.request.user
        pays_cote_ivoire = Pays.objects.get(nom="Nigeria")  # Remplacez par le pays souhaité
        form.instance.pays = pays_cote_ivoire

        dossier.save()

        # Récupérer l'email de l'agent de sélection et des chefs
        agent_selection_email = dossier.agent_selection.email
        chefs_emails = [chef.email for chef in Personnel.objects.filter(Personnel_type='chef')]

        # Préparation de l'email
        subject = 'Nouveau dossier assigné'
        message = f"""
        <html>
            <body>
                <p>Un nouveau dossier <strong>{dossier.projet}</strong> vous a été assigné par : <strong>{self.request.user}</strong> à l'agent de sélection <strong>{dossier.agent_selection}</strong>.</p>
                <p>Vous pouvez consulter le dossier en vous rendant sur l'application : <a href="https://empotage-oils-of-africa.net/login/">Cliquez ici pour vous connecter</a>.</p>
            </body>
        </html>
        """

        # Expéditeur : email de la secrétaire
        from_email = self.request.user.email

        # Liste des destinataires
        recipient_list = [agent_selection_email] + chefs_emails

        # Création de l'email
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.content_subtype = 'html'  # Spécifier le format HTML de l'email

        # Gestion des fichiers joints
        fichiers = self.request.FILES.getlist('fichiers')  # Récupérer tous les fichiers sélectionnés
        if fichiers:
            for fichier in fichiers:
                email.attach(fichier.name, fichier.read(), fichier.content_type)
        else:
            message += "<p><em>Aucun fichier joint n'a été ajouté.</em></p>"

        # Envoi de l'email
        email.send(fail_silently=False)

        # Message de succès après sauvegarde
        messages.success(self.request, "ENREGISTREMENT DU DOSSIER AVEC SUCCÈS")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Afficher les erreurs dans la console pour debug
        print(form.errors)  
        response = super().form_invalid(form)
        messages.error(self.request, "ERREUR !!! Le dossier existe déjà")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['method'] = "post"
        context['action'] = "create"  # Ajouter une variable pour indiquer l'action
        return context
    

@method_decorator(login_required, name='dispatch')
class DossierUpdateNigeriaView(UpdateView):
    model = Dossier
    form_class = DossiersNigeriaForm
    template_name = "pages/Dossier/Dossier_create_Nigeria.html"
    success_url = reverse_lazy('Dossier_list_Nigeria')

    def get_object(self, **kwargs):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Dossier, pk=pk)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()  # Passer l'instance à modifier
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Modification effectuée avec succès !")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Erreur lors de la modification du dossier.")
        return super().form_invalid(form)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['method'] = "post"
        context['action'] = "update"  # Ajouter une variable pour indiquer l'action
        return context



@method_decorator(login_required, name='dispatch')
class DossierDeleteNigeriaView( DeleteView):
    model = Dossier
    template_name = "pages/Dossier/Dossier_confirm_delete_Nigeria.html"
    success_url = reverse_lazy('Dossier_list_nigeria')
    form_invalid_message = "Oups, quelque chose s'est mal passé lors de la suppression!"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Le Dossier a été supprimé avec succès!")
        return super().delete(request, *args, **kwargs)

    def get_object(self, **kwargs):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Dossier, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['method'] = "delete"
        return context
    
# """
# # from django.views.generic import DetailView

# # class DossierDetailView(DetailView):
# #     model = Dossier
# #     template_name =  "pages/Dossier/Dossier_detail.html"


# # from django.views.generic.edit import CreateView
# # from django.shortcuts import get_object_or_404


# # class AjouterConteneurView(CreateView):
# #     model = Conteneur
# #     fields = ['reference', 'etat', 'photo_devant', 'photo_derriere', 'photo_interieur', 'numero_pieds', 'poids_brute', 'poids_equipements', 'poids_net']
# #     template_name =  "pages/Dossier/Dossier_ajouter_conteneur.html"

# #     def form_valid(self, form):
# #         # Associer le conteneur au dossier
# #         dossier = get_object_or_404(Dossier, pk=self.kwargs['dossier_id'])
# #         form.instance.dossier = dossier
# #         form.instance.agent_selection = self.request.user  # L'agent de sélection actuel
# #         return super().form_valid(form)

# #     def get_success_url(self):
# #         # Rediriger vers la page des détails du dossier après l'ajout d'un conteneur
# #         return reverse('dossier_detail', kwargs={'pk': self.kwargs['dossier_id']})


# # from django.views.generic import View
# # from django.shortcuts import redirect
# # from django.contrib import messages

# # class ValiderDossierView(View):
# #     def post(self, request, pk, *args, **kwargs):
# #         dossier = get_object_or_404(Dossier, pk=pk)

# #         # Vérifier s'il y a au moins un conteneur ajouté avant la validation
# #         if dossier.conteneurs_selection.exists():
# #             dossier.statut = 'finalisation_en_cours'  # Changer le statut du dossier
# #             dossier.save()
# #             messages.success(request, 'Le dossier a été validé avec succès.')
# #         else:
# #             messages.error(request, 'Vous devez ajouter au moins un conteneur avant de valider.')

# #         return redirect('dossier_detail', pk=pk)
# # """

    
    
def dossier_detail_Nigeria(request, pk):
    dossier = get_object_or_404(Dossier, pk=pk)
    return render(request, 'pages/Dossier/Dossier_detail_modal_nigeria.html', {'dossier': dossier})