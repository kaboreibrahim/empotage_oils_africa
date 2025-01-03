#from django.http import HttpRequest, HttpResponseRedirect
from django.db import IntegrityError
from django.views.generic import ListView, CreateView,UpdateView,DeleteView
from conteneurs.models import *
from conteneurs.forms import ConteneurAcconageForm
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import FormView
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML
from django.templatetags.static import static

from django.contrib.auth.models import User

from django.db.models import Q

class DossierAccoangeListView(LoginRequiredMixin, ListView):
    model = Dossier
    template_name = 'pages/Dossier_Acconage/dossier_list_Acconage.html'  # Template to be created
    context_object_name = 'Dossier_list'

    def get_context_data(self, **kwargs):
        """
        Adds additional context for dossiers in acconage process and awaiting acconage.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Filter dossiers based on status for the current user
        context['dossier_acconage_en_cours'] = Dossier.objects.filter(
            agent_acconage=user,
            statut='ACCONAGE_FAIT'
        ).order_by('-Date_ajout')
        context['dossier_en_attente_acconage'] = Dossier.objects.filter(
            agent_acconage=user,
            statut='Aconage_en_cours'
        ).order_by('-Date_ajout')

        # Check if the user is 'Responsable'
        if user.username == 'Responsable':
            # Add dossiers for 'Responsable'
            context['dossier_acconage_en_cours'] |= Dossier.objects.filter(
                statut='ACCONAGE_FAIT'
            ).order_by('-Date_ajout')
            context['dossier_en_attente_acconage'] |= Dossier.objects.filter(
                statut='Aconage_en_cours'
            ).order_by('-Date_ajout')

        return context

def manage_conteneurs_acconage(request, dossier_id, conteneur_id):
    print(f"dossier_id: {dossier_id}")  # Instruction de débogage
    print(f"conteneur_id: {conteneur_id}")  # Instruction de débogage
    conteneur = get_object_or_404(Conteneur, id=conteneur_id)

    if request.method == 'POST':
        form = ConteneurAcconageForm(request.POST, request.FILES, instance=conteneur)
        if form.is_valid():
            conteneur = form.save(commit=False)
            conteneur.agent_acconage = request.user  # Assigne l'agent d'acconage
            conteneur.save()
            conteneur.dossier.marquer_comme_acconage_fait()
            
            # Met à jour le statut du dossier si nécessaire
            conteneur.verifier_et_changer_statut()
            return redirect('view_conteneurs', dossier_id=dossier_id)
        else:
            print(form.errors)  # Affiche les erreurs de validation pour le débogage
    else:
        form = ConteneurAcconageForm(instance=conteneur)

    return render(request, 'pages/Dossier_Acconage/conteneur_ajout.html', {
        'form': form,
        'conteneur': conteneur,
        'dossier_id': dossier_id
    })



def afficher_detail_conteneur(request, conteneur_id):
    # Récupérer le conteneur ou renvoyer une erreur 404 s'il n'existe pas
    conteneur = get_object_or_404(Conteneur, id=conteneur_id)
    
    # Passer les détails du conteneur au template
    return render(request, 'pages/Dossier_Acconage/detail_conteneur.html', {'conteneur': conteneur})



def modifier_conteneur(request, conteneur_id,dossier_id):
    # Récupérer l'objet conteneur en utilisant l'ID fourni, ou renvoyer une erreur 404 s'il n'existe pas
    conteneur = get_object_or_404(Conteneur, id=conteneur_id)
    
    if request.method == 'POST':
        # Si la méthode est POST, cela signifie que le formulaire est soumis
        form = ConteneurAcconageForm(request.POST, request.FILES, instance=conteneur)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conteneur mis à jour avec succès !')
            return redirect('view_conteneurs', dossier_id=dossier_id)
    else:
        # Si la méthode est GET, afficher le formulaire avec les données du conteneur existant
        form = ConteneurAcconageForm(instance=conteneur)

    context = {
        'form': form,
        'conteneur': conteneur,
        'dossier_id': dossier_id

    }
    return render(request, 'pages/Dossier_Acconage/modifier_conteneur.html', context)



"""def generate_dossier_aconage_pdf(request, dossier_id):
    dossier = Dossier.objects.get(id=dossier_id)
    conteneurs = dossier.conteneurs.all()

    # URL absolue du logo
    logo_url = request.build_absolute_uri(static('img/logo.jpg'))  # Utiliser une URL absolue

    # Charger le template HTML
    template = get_template('pages/Dossier_Acconage/pdf_selection_aconage.html')
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
        'Date_ajout': dossier.Date_ajout,
        'Date_selection': dossier.Date_selection,
        'Date_acconage': dossier.Date_acconage,
        'Date_terminer': dossier.Date_terminer,
        'logo_url': logo_url  # Passer l'URL absolue du logo au template
    })

    # Convertir en PDF
    pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf()

    # Retourner le fichier PDF en réponse HTTP
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Rapport habillage & empotage {dossier.projet}.pdf"'
    return response
    
""" 


def format_date(date):
    if date:
        return date.strftime("%Y-%m-%d %A %H:%M")
    return "N/A"

 
import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def generate_dossier_aconage_pdf(request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)
    conteneurs = dossier.conteneurs.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Rapport habillage & empotage {dossier.projet}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=landscape(letter),
                            rightMargin=0.5*inch, leftMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    normal_style = styles['Normal']

    # Contenu du document
    elements = []

    # Logo
    logo_path = os.path.join(settings.STATIC_ROOT, 'img/logo.jpg')
    elements.append(Paragraph(f'<img src="{logo_path}" width="70" height="70" />', normal_style))
    elements.append(Spacer(1, 0.2*inch))

    # Titre et informations du dossier
    elements.append(Paragraph(f"Rapport D'habillage & empotage Du Dossier: {dossier.projet}", title_style))
    elements.append(Spacer(1, 0.1*inch))

    info_text = [
        f"Client: {dossier.client}",
        f"TRD: {dossier.TRD}",
        f"BOOKING: {dossier.booking}",
        f"Site de sélection: {dossier.site}",
        f"Site d'habillage & empotage: {dossier.Site_empotage}",
        f"Nom de l'agent de sélection: Mr {dossier.agent_selection} - tel :{dossier.agent_selection.Contact}",
        f"Nom de l'agent d'habillage et empotage: ({dossier.agent_acconage}) Mr {dossier.agent_acconage.first_name} {dossier.agent_acconage.last_name} - tel :{dossier.agent_acconage.Contact}",
        f"Compagnie maritime: {dossier.compagnie_maritime}",
        f"POD: {dossier.port_de_dechargement}",
        f"POL: {dossier.port_de_chargement}",
        f"Commodité: {dossier.commodite}",
        f"Date d'ajout: {dossier.Date_ajout.strftime('%Y-%m-%d %H:%M')}",
        f"Date de sélection: {dossier.Date_selection.strftime('%Y-%m-%d %H:%M') if dossier.Date_selection else 'Non défini'}",
        f"Date d'acconage: {dossier.Date_acconage.strftime('%Y-%m-%d %H:%M') if dossier.Date_acconage else 'Non défini'}",
        f"Date de fin: {dossier.Date_terminer.strftime('%Y-%m-%d %H:%M') if dossier.Date_terminer else 'Non défini'}",

        f"Nombre de conteneurs: {conteneurs.count()}"
    ]

    for line in info_text:
        elements.append(Paragraph(line, normal_style))
        elements.append(Spacer(1, 0.05*inch))

    elements.append(Spacer(1, 0.2*inch))

    # Tableau des conteneurs
    data = [["N°", "Réf", "État", "P.brute", "P.équipement", "P.net", "heating pad", "flexitank", "plomb"]]
    for i, conteneur in enumerate(conteneurs, start=1):
        data.append([
            i,
            conteneur.reference or "N/A",
            conteneur.etat or "N/A",
            f"{conteneur.poids_brute or 'N/A'} KG",
            f"{conteneur.poids_equipements or 'N/A'} KG",
            f"{conteneur.poids_net or 'N/A'} KG",
            conteneur.numero_heating_pad or "N/A",
            conteneur.numero_flexitank or "N/A",
            conteneur.numero_plomb or "N/A"
        ])

    table = Table(data)
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

    # Générer le PDF
    doc.build(elements)

    return response


def soumettre_dossier_acconage(request, dossier_id):
    # Récupérer le dossier
    dossier = get_object_or_404(Dossier, id=dossier_id)

    # Vérifier si tous les conteneurs du dossier ont le statut 'acconé'
    conteneurs = Conteneur.objects.filter(dossier=dossier)

    if not conteneurs.exists():
        messages.error(request, "Aucun conteneur n'est associé à ce dossier.")
        return redirect('dossier_list_Accoange')

    # Vérifier que tous les conteneurs ont le statut 'acconé'
    conteneurs_non_accones = conteneurs.exclude(statut='aconer')
    if conteneurs_non_accones.exists():
        messages.error(request, "Tous les conteneurs doivent avoir le statut 'habillage et empotage' avant de soumettre le dossier.")
        return redirect('view_conteneurs', dossier_id=dossier_id)

    # Si le dossier a déjà été soumis (statut 'ACCONAGE_FAIT'), le soumettre
    if dossier.statut == 'ACCONAGE_FAIT':
        # Changer le statut du dossier
        dossier.terminer_dossier()
        dossier.Date_terminer = timezone.now()
        dossier.save()

        # Récupérer les emails des personnes concernées
        emails = []
        if dossier.agent_acconage:
            emails.append(dossier.agent_acconage.email)
        if dossier.secretaire:
            emails.append(dossier.secretaire.email)

        # Récupérer les emails de tous les chefs
        chefs = Personnel.objects.filter(Personnel_type='chef')
        chefs_emails = [chef.email for chef in chefs]

        # Ajouter les emails des chefs à la liste des destinataires
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

        # Utiliser l'email de l'agent d'acconage connecté comme expéditeur
        from_email = request.user.email

        # Générer le PDF
        pdf_response = generate_dossier_aconage_pdf(request, dossier_id)
        pdf_content = pdf_response.content

        # Créer et envoyer l'e-mail avec le PDF en pièce jointe
        email = EmailMultiAlternatives(
            subject=f"Dossier {dossier.projet} - Habillage & empotage Terminé",
            body=(
                f"<html>"
                f"<body>"
                f"<p>Le dossier <strong>{dossier.projet}</strong> (TRD: {dossier.TRD}) a terminé Habillage & empotage, "
                f"transmis par l'agent de sélection {request.user.username}.</p>"
                f"<p>Veuillez trouver ci-joint le PDF avec les détails du dossier et des conteneurs.</p>"
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
            messages.success(request, f"Dossier {dossier.projet} soumis avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'envoi de l'email : {str(e)}")
    else:
        # Si le dossier n'est pas dans le bon état, afficher une erreur
        messages.error(request, "Le dossier n'est pas dans un état valide pour être soumis.")

    # Redirection vers la liste des dossiers
    return redirect('dossier_list_Accoange')

    
def retrograder_dossier (request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)
        
    dossier.retrograder_en_selection()
    messages.success(request, f"Le dossier {dossier.projet} a été rétrogradé avec succès.")
    return redirect('dossier_list_Accoange')
