#from django.http import HttpRequest, HttpResponseRedirect
from django.db import IntegrityError
from django.views.generic import ListView, CreateView,UpdateView,DeleteView
from conteneurs.models import *
from conteneurs.forms import ConteneurForm, ConteneurFormSet
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import FormView
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.templatetags.static import static
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML
from django.templatetags.static import static

class DossierSelectionListView(LoginRequiredMixin, ListView):
    model = Dossier
    template_name = 'pages/Dossier_selection/dossier_list.html'
    context_object_name = 'dossiers'

    def get_queryset(self):
        """
        Retourne les dossiers où l'agent de sélection connecté est associé,
        excluant ceux en 'Aconage_en_cours'.
        """
        user = self.request.user
        if user.username == 'Responsable':
            return Dossier.objects.exclude(statut='Aconage_en_cours').order_by('-Date_ajout')
        else:
            return Dossier.objects.filter(agent_selection=user).exclude(statut='Aconage_en_cours').order_by('-Date_ajout')

    def get_context_data(self, **kwargs):
        """
        Ajoute les contextes supplémentaires pour les dossiers en attente et en cours de sélection.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.username == 'Responsable':
            context['dossiers_en_attente'] = Dossier.objects.filter(statut='en_attente').order_by('-Date_ajout')
            context['dossiers_en_cours'] = Dossier.objects.filter(statut='selection_en_cours').order_by('-Date_ajout')
        else:
            context['dossiers_en_attente'] = Dossier.objects.filter(agent_selection=user, statut='en_attente').order_by('-Date_ajout')
            context['dossiers_en_cours'] = Dossier.objects.filter(agent_selection=user, statut='selection_en_cours').order_by('-Date_ajout')

        return context

def view_conteneurs(request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)
    conteneurs = Conteneur.objects.filter(dossier=dossier).order_by('-Date_ajout')

    return render(request, 'pages/Dossier_selection/view_conteneur.html', {
        'conteneurs': conteneurs,
        'dossier': dossier
    })


def manage_conteneurs(request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)

    ConteneurFormSet = modelformset_factory(
        Conteneur,
        form=ConteneurForm,
        extra=1,
        can_delete=True
    )

    if request.method == 'POST':
        formset = ConteneurFormSet(request.POST, request.FILES, queryset=Conteneur.objects.filter(dossier=dossier))
        if formset.is_valid():
            conteneurs = formset.save(commit=False)
            for form in formset.deleted_forms:
                if form.instance.pk:
                    form.instance.delete()
            for conteneur in conteneurs:
                conteneur.dossier = dossier
                conteneur.agent_selection = request.user
                conteneur.save()
            dossier.envoyer_pour_selection()  # Met à jour le statut du dossier si nécessaire
            return redirect('view_conteneurs', dossier_id=dossier_id)
        else:
            print(formset.errors)  # Affiche les erreurs de validation pour le débogage
    else:
        # Assurez-vous d'obtenir uniquement les conteneurs qui ne sont pas liés au dossier
        formset = ConteneurFormSet(queryset=Conteneur.objects.none())


    return render(request, 'pages/Dossier_selection/conteneur_create.html', {
        'formset': formset,
        'dossier': dossier
    })



class ConteneurUpdateView(LoginRequiredMixin, UpdateView):
    model = Conteneur
    form_class = ConteneurForm
    template_name = 'pages/Dossier_selection/modifier_conteneur.html'

    def get_success_url(self):
        # Obtenir le conteneur mis à jour
        conteneur = self.object
        dossier_id = conteneur.dossier.id
        # Rediriger vers la vue des conteneurs du dossier
        return reverse_lazy('view_conteneurs', kwargs={'dossier_id': dossier_id})

    def get_object(self, queryset=None):
        return get_object_or_404(Conteneur, id=self.kwargs['pk'])
    

class ConteneurDeleteView(LoginRequiredMixin, DeleteView):
    model = Conteneur
    template_name = 'pages/Dossier_selection/conteneur_confirm_delete.html'
    success_url = reverse_lazy('dossier_list_selction')  # Ou une URL spécifique à ta vue
    
    def get_success_url(self):
        # Obtenir le conteneur mis à jour
        conteneur = self.object
        dossier_id = conteneur.dossier.id
        # Rediriger vers la vue des conteneurs du dossier
        return reverse_lazy('view_conteneurs', kwargs={'dossier_id': dossier_id})

    def get_object(self, queryset=None):
        return get_object_or_404(Conteneur, id=self.kwargs['pk'])




"""def generate_dossier_pdf(request, dossier_id):
    dossier = Dossier.objects.get(id=dossier_id)
    conteneurs = dossier.conteneurs.all()

    # URL absolue du logo
    logo_url = request.build_absolute_uri(static('img/logo.jpg'))  # Utiliser une URL absolue

    # Charger le template HTML
    template = get_template('pages/Dossier_selection/pdf_selection.html')
    html_content = template.render({
        'projet': dossier.projet,
        'client': dossier.client,
        'TRD': dossier.TRD,
        'compagnie_maritime': dossier.compagnie_maritime,
        'port_de_dechargement': dossier.port_de_dechargement,
        'port_de_chargement': dossier.port_de_chargement,
        'commodite': dossier.commodite,
        'conteneurs': conteneurs,
        'site': dossier.site,
        'Site_empotage': dossier.Site_empotage,
        'agent_selection': dossier.agent_selection,
        'agent_acconage': dossier.agent_acconage,
        'logo_url': logo_url  # Passer l'URL absolue du logo au template
    })

    # Convertir en PDF
    pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf()

    # Retourner le fichier PDF en réponse HTTP
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Rapport de selection {dossier.projet}.pdf"'
    return response
"""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from urllib.parse import quote
import os

def generate_dossier_pdf(request, dossier_id):
    """
    Génère un rapport PDF pour un dossier spécifique.
    
    Args:
        request: La requête HTTP
        dossier_id: L'identifiant du dossier
    
    Returns:
        HttpResponse: Le fichier PDF généré
    """
    # --- Récupération des données ---
    dossier = get_object_or_404(Dossier, id=dossier_id)
    conteneurs = dossier.conteneurs.all()

    # --- Configuration de la réponse HTTP ---
    response = HttpResponse(content_type='application/pdf')
    filename = _generate_filename(dossier)
    response['Content-Disposition'] = f'attachment; filename="{quote(filename)}"'

    # --- Configuration du document PDF ---
    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    # --- Génération du contenu ---
    elements = []
    styles = getSampleStyleSheet()
    
    # Création d'un style pour les sous-titres
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=6
    )
    
    # Ajout du logo
    _add_logo(elements, styles['Normal'])
    
    # Ajout du titre et des informations
    _add_header_info(elements, dossier, styles, subtitle_style)
    
    # Ajout du tableau des conteneurs
    _add_containers_table(elements, conteneurs, dossier, styles['Normal'])

    # --- Génération finale du PDF ---
    doc.build(elements)
    return response

def _generate_filename(dossier):
    """Génère le nom du fichier en fonction du type de conteneur."""
    if dossier.type_conteneur == 'ISO_20_pieds':
        return f"Rapport de selection des ISOTANKS Du Dossier {dossier.projet}.pdf"
    return f"Rapport de selection des Conteneurs Du Dossier{dossier.projet}.pdf"

def _add_logo(elements, normal_style):
    """Ajoute le logo au document."""
    logo_path = os.path.join(settings.STATIC_ROOT, 'img/logo.jpg')
    elements.append(Paragraph(f'<img src="{logo_path}" width="70" height="70" />', normal_style))
    elements.append(Spacer(1, 0.2*inch))

def _add_header_info(elements, dossier, styles, subtitle_style):
    """Ajoute le titre et les informations catégorisées du dossier."""
    # Titre principal
    title_text = _generate_title(dossier)
    elements.append(Paragraph(title_text, styles['Heading1']))
    elements.append(Spacer(1, 0.2*inch))

    # Informations du Projet
    elements.append(Paragraph("Informations du Projet", subtitle_style))
    project_info = [
        f"Projet: {dossier.projet}",
        f"TRD: {dossier.TRD}",
        f"Booking: {dossier.booking}",
        f"Client: {dossier.client}"
    ]
    _add_info_section(elements, project_info, styles['Normal'])

    # Détails des Conteneurs
    elements.append(Paragraph("Détails des Conteneurs", subtitle_style))
    container_info = [
        f"Type de Conteneur: {dossier.get_type_conteneur_display()}",
        f"Commodité: {dossier.commodite}",
        f"Nombre de conteneurs: {dossier.conteneurs.count()}"
    ]
    _add_info_section(elements, container_info, styles['Normal'])

    # Localisation
    elements.append(Paragraph("Localisation", subtitle_style))
    location_info = [
        f"Site de sélection: {dossier.site}",
        f"Site d'habillage & empotage: {dossier.Site_empotage}"
    ]
    _add_info_section(elements, location_info, styles['Normal'])

    # Informations Maritimes
    elements.append(Paragraph("Informations Maritimes", subtitle_style))
    maritime_info = [
        f"Compagnie maritime: {dossier.compagnie_maritime}",
        f"Port de chargement (POL): {dossier.port_de_chargement}",
        f"Port de déchargement (POD): {dossier.port_de_dechargement}"
    ]
    _add_info_section(elements, maritime_info, styles['Normal'])

    # Agents et Clients
    elements.append(Paragraph("Agents et Clients", subtitle_style))
    agent_info = [
        f"Agent de sélection: Mr {dossier.agent_selection} - Tel: {dossier.agent_selection.Contact}",
        f"Agent d'habillage et empotage: Mr {dossier.agent_acconage.first_name} {dossier.agent_acconage.last_name} - Tel: {dossier.agent_acconage.Contact}"
    ]
    _add_info_section(elements, agent_info, styles['Normal'])

    # Dates Importantes
    elements.append(Paragraph("Dates Importantes", subtitle_style))
    date_info = [
        f"Date d'ajout: {dossier.Date_ajout.strftime('%Y-%m-%d %H:%M')}",
        f"Date de sélection: {dossier.Date_selection.strftime('%Y-%m-%d %H:%M')}"
    ]
    _add_info_section(elements, date_info, styles['Normal'])

def _add_info_section(elements, info_list, style):
    """Ajoute une section d'informations avec l'espacement approprié."""
    for line in info_list:
        elements.append(Paragraph(line, style))
        elements.append(Spacer(1, 0.05*inch))
    elements.append(Spacer(1, 0.1*inch))

def _generate_title(dossier):
    """Génère le titre du rapport en fonction du type de conteneur."""
    if dossier.type_conteneur == 'ISO_20_pieds':
        return f"Rapport de sélection des ISO TANKS Du Dossier: {dossier.projet}({dossier.pays})"
    return f"Rapport de sélection des Conteneurs Du Dossier: {dossier.projet}({dossier.pays})"

def _add_containers_table(elements, conteneurs, dossier, normal_style):
    """Ajoute le tableau des conteneurs au document."""
    elements.append(Paragraph("Liste des Conteneurs", normal_style))
    elements.append(Spacer(1, 0.1*inch))

    data = [["N°", "Réf", "État", "Type"]]
    
    for i, conteneur in enumerate(conteneurs, start=1):
        data.append([
            i,
            conteneur.reference or "N/A",
            conteneur.etat or "N/A",
            dossier.get_type_conteneur_display()
        ])

    table = Table(data, colWidths=[1*inch, 2*inch, 2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)

    # Génération du PDF
    doc.build(elements)

    return response



def soumettre_dossier(request, dossier_id):
    # Récupérer le dossier
    dossier = get_object_or_404(Dossier, id=dossier_id)

    # Vérifier le statut du dossier
    if dossier.statut == 'selection_en_cours':
        # Changer le statut du dossier
        dossier.statut = 'Aconage_en_cours'
        dossier.statut_date = timezone.now()
        dossier.save()

        # Récupérer les emails des personnes concernées
        emails = []
        if dossier.agent_acconage:
            emails.append(dossier.agent_acconage.email)
        if dossier.secretaire:
            emails.append(dossier.secretaire.email)

        # Récupérer les emails de tous les personnels ayant le statut 'chef'
        chefs_emails = [chef.email for chef in Personnel.objects.filter(Personnel_type='chef')]
        emails += chefs_emails

        # Emails à mettre en copie (CC)
        cc_emails = [
            'alice.tuo@oils-of-africa.ci',
            'appro.stock@oils-of-africa.ci',
            'fitting.loadingassistance1@oils-of-africa.ci',
            'ops@africa-newportlogistics.ci',
            'import.export@africa-newportlogistics.ci',
            'stagiaireoils@gmail.com'
        ]

        # Utiliser l'email de l'utilisateur connecté comme expéditeur
        from_email = request.user.email

        # Générer le PDF
        pdf_response = generate_dossier_pdf(request, dossier_id)
        pdf_content = pdf_response.content

        # Créer et envoyer l'e-mail avec le PDF en pièce jointe
        email = EmailMultiAlternatives(
            subject=f"Dossier {dossier.projet} - Prêt pour l'habillage & l'empotage",
            body=(
                f"<html>"
                f"<body>"
                f"<p>Le dossier <strong>{dossier.projet}</strong> (TRD: {dossier.TRD}) a été envoyé par "
                f"l'agent de sélection : {request.user.username}. Veuillez trouver ci-joint le PDF avec les "
                f"détails du dossier et des conteneurs.</p>"
                f"<p>Pour plus de détails, veuillez visiter le lien suivant : "
                f"<a href='https://empotage-oils-of-africa.net/login/'>Cliquez ici pour vous connecter</a>.</p>"
                f"</body>"
                f"</html>"
            ),
            from_email=from_email,
            to=emails,
            cc=cc_emails
        )
        
        # Joindre le PDF
        email.attach('dossier_details.pdf', pdf_content, 'application/pdf')

        # Indiquer que l'email est en HTML
        email.content_subtype = 'html'

        # Envoyer l'email
        try:
            email.send()
            messages.success(request, f"Dossier {dossier.projet} soumis avec succès à l'agent d'empotage.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'envoi de l'email : {str(e)}")
    else:
        # Si le dossier n'est pas dans le bon état, afficher une erreur
        messages.error(request, "Le dossier n'est pas dans un état valide pour être soumis.")

    # Redirection vers la liste des dossiers
    return redirect('dossier_list_selction')