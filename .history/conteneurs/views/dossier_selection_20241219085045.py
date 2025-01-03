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

# from reportlab.lib import colors
# from reportlab.lib.units import inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.pagesizes import landscape, letter  # Add this line
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404
# import os
# from django.conf import settings
# from urllib.parse import quote

# def generate_dossier_pdf(request, dossier_id):
#     dossier = get_object_or_404(Dossier, id=dossier_id)
#     conteneurs = dossier.conteneurs.all()

#     response = HttpResponse(content_type='application/pdf')

#     # Condition pour le nom du fichier
#     if dossier.type_conteneur == 'ISO_20_pieds':  # Condition pour type ISO
#         filename = f"Rapport de selection des ISOTANKS Du Dossier {dossier.projet}.pdf"
#     else:
#         filename = f"Rapport de selection des Conteneurs Du Dossier{dossier.projet}.pdf"

#     # Encodage pour éviter les erreurs avec des navigateurs
#     response['Content-Disposition'] = f'attachment; filename="{quote(filename)}"'

#     # Configuration du PDF
#     doc = SimpleDocTemplate(response, pagesize=landscape(letter),
#                             rightMargin=0.5*inch, leftMargin=0.5*inch,
#                             topMargin=0.5*inch, bottomMargin=0.5*inch)

#     # Styles
#     styles = getSampleStyleSheet()
#     title_style = styles['Heading1']
#     normal_style = styles['Normal']

#     # Contenu du document
#     elements = []

#     # Logo
#     logo_path = os.path.join(settings.STATIC_ROOT, 'img/logo.jpg')
#     elements.append(Paragraph(f'<img src="{logo_path}" width="70" height="70" />', normal_style))
#     elements.append(Spacer(1, 0.2*inch))

#     # Titre et informations du dossier
#     if dossier.type_conteneur == 'ISO_20_pieds':  # Condition pour type ISO
#         title_text = f"Rapport de sélection des ISO TANKS Du Dossier: {dossier.projet}({dossier.pays})"
#     else:
#         title_text = f"Rapport de sélection des Conteneurs Du Dossier: {dossier.projet}({dossier.pays})"

#     elements.append(Paragraph(title_text, title_style))

#     elements.append(Spacer(1, 0.1*inch))

#     info_text = [
#         f"Client: {dossier.client}",
#         f"TRD: {dossier.TRD}",
#         f"BOOKING: {dossier.booking}",
#         f"Site de sélection: {dossier.site}",
#         f"Site d'habillage & empotage: {dossier.Site_empotage}",
#         f"Nom de l'agent de sélection: Mr {dossier.agent_selection} - tel :{dossier.agent_selection.Contact}",
#         f"Nom de l'agent d'habillage et empotage: ({dossier.agent_acconage}) Mr {dossier.agent_acconage.first_name} {dossier.agent_acconage.last_name} - tel :{dossier.agent_acconage.Contact}",
#         f"Compagnie maritime: {dossier.compagnie_maritime}",
#         f"POD: {dossier.port_de_dechargement}",
#         f"POL: {dossier.port_de_chargement}",
#         f"Commodité: {dossier.commodite}",
#         f"Date d'ajout: {dossier.Date_ajout.strftime('%Y-%m-%d %H:%M')}",
#         f"Date de sélection: {dossier.Date_selection.strftime('%Y-%m-%d %H:%M')}",
#         f"Nombre de conteneurs: {conteneurs.count()}"
#     ]

#     for line in info_text:
#         elements.append(Paragraph(line, normal_style))
#         elements.append(Spacer(1, 0.05*inch))

#     elements.append(Spacer(1, 0.2*inch))

#     # Tableau des conteneurs
#     data = [["N°", "Réf", "État", "Type"]]
#     for i, conteneur in enumerate(conteneurs, start=1):
#         data.append([
#             i,
#             conteneur.reference or "N/A",
#             conteneur.etat or "N/A",
#             dossier.get_type_conteneur_display()
#         ])

#     table = Table(data, colWidths=[1*inch, 2*inch, 2*inch, 2*inch])
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('FONTSIZE', (0, 0), (-1, 0), 12),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#     ]))

#     # Ajout du tableau au document
#     elements.append(Spacer(1, 0.2*inch))
#     elements.append(Paragraph('<br/>', normal_style))
#     elements.append(table)

#     # Génération du PDF
#     doc.build(elements)

#     return response

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepInFrame
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from urllib.parse import quote
import os

class ContainerReportTemplate(PageTemplate):
    def __init__(self, parent):
        page_width = parent.pagesize[0]
        page_height = parent.pagesize[1]
        left_margin = right_margin = 0.5*inch
        column_width = (page_width - left_margin - right_margin - 0.5*inch) / 2
        
        # Frame pour les colonnes d'information (partie supérieure)
        frame1 = Frame(
            left_margin, 
            page_height * 0.4,  # Réserve 40% de la page pour le tableau
            column_width,
            page_height * 0.6 - inch,  # Hauteur ajustée
            id='col1'
        )
        frame2 = Frame(
            left_margin + column_width + 0.5*inch,
            page_height * 0.4,  # Réserve 40% de la page pour le tableau
            column_width,
            page_height * 0.6 - inch,  # Hauteur ajustée
            id='col2'
        )
        
        # Frame pour le tableau (partie inférieure)
        table_frame = Frame(
            left_margin,
            inch,  # Marge du bas
            page_width - 2*left_margin,
            page_height * 0.35,  # 35% de la hauteur pour le tableau
            id='table'
        )
        
        frames = [frame1, frame2, table_frame]
        PageTemplate.__init__(self, 'ThreePartLayout', frames=frames)

class ContainerReportDocument(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self.addPageTemplates(ContainerReportTemplate(self))

    def build(self, left_elements, right_elements, table_elements):
        """Construit le document avec les éléments dans leurs frames respectives."""
        story = []
        
        # Encapsule les éléments de gauche et de droite dans KeepInFrame
        story.append(KeepInFrame(
            content=left_elements,
            maxWidth=self._calc_frame_width('col1'),
            maxHeight=self._calc_frame_height('col1')
        ))
        story.append(KeepInFrame(
            content=right_elements,
            maxWidth=self._calc_frame_width('col2'),
            maxHeight=self._calc_frame_height('col2')
        ))
        story.append(KeepInFrame(
            content=table_elements,
            maxWidth=self._calc_frame_width('table'),
            maxHeight=self._calc_frame_height('table')
        ))
        
        BaseDocTemplate.build(self, story)

    def _calc_frame_width(self, frame_id):
        """Calcule la largeur du frame spécifié."""
        template = self.pageTemplates[0]
        frame = next(f for f in template.frames if f.id == frame_id)
        return frame._width

    def _calc_frame_height(self, frame_id):
        """Calcule la hauteur du frame spécifié."""
        template = self.pageTemplates[0]
        frame = next(f for f in template.frames if f.id == frame_id)
        return frame._height

def _generate_title(dossier):
    """
    Génère le titre du rapport en fonction du type de conteneur.
    
    Args:
        dossier: L'objet dossier contenant les informations
    
    Returns:
        str: Le titre formaté du rapport
    """
    base_title = "Rapport de sélection"
    if dossier.type_conteneur == 'ISO_20_pieds':
        container_type = "des ISO TANKS"
    else:
        container_type = "des Conteneurs"
    
    return f"{base_title} {container_type} Du Dossier: {dossier.projet} ({dossier.pays})"

def _generate_filename(dossier):
    """Génère le nom du fichier."""
    if dossier.type_conteneur == 'ISO_20_pieds':
        return f"Rapport de selection des ISOTANKS Du Dossier {dossier.projet}.pdf"
    return f"Rapport de selection des Conteneurs Du Dossier {dossier.projet}.pdf"

def _add_logo(elements, normal_style):
    """Ajoute le logo."""
    logo_path = os.path.join(settings.STATIC_ROOT, 'img/logo.jpg')
    elements.append(Paragraph(f'<img src="{logo_path}" width="70" height="70" />', normal_style))
    elements.append(Spacer(1, 0.2*inch))

def _add_info_section(elements, info_list, style):
    """Ajoute une section d'informations."""
    for line in info_list:
        elements.append(Paragraph(line, style))
        elements.append(Spacer(1, 0.05*inch))
    elements.append(Spacer(1, 0.1*inch))

def _create_containers_table(conteneurs, dossier, normal_style):
    """Crée le tableau des conteneurs."""
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
    
    return table

def generate_dossier_pdf(request, dossier_id):
    """Génère un rapport PDF pour un dossier spécifique avec layout fixe."""
    dossier = get_object_or_404(Dossier, id=dossier_id)
    conteneurs = dossier.conteneurs.all()

    response = HttpResponse(content_type='application/pdf')
    filename = _generate_filename(dossier)
    response['Content-Disposition'] = f'attachment; filename="{quote(filename)}"'

    # Configuration du document avec la nouvelle classe
    doc = ContainerReportDocument(
        response,
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=6
    )

    # Création des éléments pour la colonne de gauche
    left_elements = []
    
    # En-tête (logo et titre)
    _add_logo(left_elements, styles['Normal'])
    title_text = _generate_title(dossier)
    left_elements.append(Paragraph(title_text, styles['Heading1']))
    left_elements.append(Spacer(1, 0.2*inch))

    # Informations du Projet
    left_elements.append(Paragraph("Informations du Projet", subtitle_style))
    project_info = [
        f"Projet: {dossier.projet}",
        f"TRD: {dossier.TRD}",
        f"Booking: {dossier.booking}",
        f"Client: {dossier.client}"
    ]
    _add_info_section(left_elements, project_info, styles['Normal'])

    # Détails des Conteneurs
    left_elements.append(Paragraph("Détails des Conteneurs", subtitle_style))
    container_info = [
        f"Type de Conteneur: {dossier.get_type_conteneur_display()}",
        f"Commodité: {dossier.commodite}",
        f"Nombre de conteneurs: {dossier.conteneurs.count()}"
    ]
    _add_info_section(left_elements, container_info, styles['Normal'])

    # Localisation
    left_elements.append(Paragraph("Localisation", subtitle_style))
    location_info = [
        f"Site de sélection: {dossier.site}",
        f"Site d'habillage & empotage: {dossier.Site_empotage}"
    ]
    _add_info_section(left_elements, location_info, styles['Normal'])

    # Création des éléments pour la colonne de droite
    right_elements = []

    # Informations Maritimes
    right_elements.append(Paragraph("Informations Maritimes", subtitle_style))
    maritime_info = [
        f"Compagnie maritime: {dossier.compagnie_maritime}",
        f"Port de chargement (POL): {dossier.port_de_chargement}",
        f"Port de déchargement (POD): {dossier.port_de_dechargement}"
    ]
    _add_info_section(right_elements, maritime_info, styles['Normal'])

    # Agents et Clients
    right_elements.append(Paragraph("Agents et Clients", subtitle_style))
    agent_info = [
        f"Agent de sélection: Mr {dossier.agent_selection} - Tel: {dossier.agent_selection.Contact}",
        f"Agent d'habillage et empotage: Mr {dossier.agent_acconage.first_name} {dossier.agent_acconage.last_name} - Tel: {dossier.agent_acconage.Contact}"
    ]
    _add_info_section(right_elements, agent_info, styles['Normal'])

    # Dates Importantes
    right_elements.append(Paragraph("Dates Importantes", subtitle_style))
    date_info = [
        f"Date d'ajout: {dossier.Date_ajout.strftime('%Y-%m-%d %H:%M')}",
        f"Date de sélection: {dossier.Date_selection.strftime('%Y-%m-%d %H:%M')}"
    ]
    _add_info_section(right_elements, date_info, styles['Normal'])

    # Création des éléments pour le tableau
    table_elements = []
    table_elements.append(Paragraph("Liste des Conteneurs", styles['Heading2']))
    table_elements.append(Spacer(1, 0.1*inch))
    table_elements.append(_create_containers_table(conteneurs, dossier, styles['Normal']))

    # Génération du PDF avec les éléments séparés
    doc.build(left_elements, right_elements, table_elements)
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