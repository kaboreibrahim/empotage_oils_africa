from email.message import EmailMessage
from django.db import models
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os.path
import uuid
from django.utils import timezone
import random
from django_lifecycle import LifecycleModel
from django.core.mail import send_mail
from reportlab.lib import colors
imageFs = FileSystemStorage(location=os.path.join(str(settings.BASE_DIR),
                                                 '/medias/'))
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from io import BytesIO
import os
from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO
from django.http import HttpResponse
import os
from django.conf import settings
from django.templatetags.static import static
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.core.mail import EmailMessage

from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML

class Pays(SafeDeleteModel,LifecycleModel):
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    _safedelete_policy = SOFT_DELETE_CASCADE
    nom = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nom
    
    
class Personnel(AbstractUser, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    USER_TYPE_CHOICES = [
        ('agent_selection', 'Agent de Sélection '),
        ('agent_acconage', 'Agent Habillage & empotage'),
        ('secretaire', 'Secrétaire'),
        ('chef', 'Chef'),
    ]
    USER_PAYS = [
        ("côte_ivoire",  "côte_ivoire"),
        ('Ghana', 'Ghana'),
        ('Nigeria', 'Nigeria'),
        ('Benin', 'Benin'),
        ('Gabon', 'Gabon'),
    ]
    Contact = models.CharField(max_length=20)
    photos = models.ImageField("Photo", upload_to='Proprietaire_photos/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    Personnel_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    Personnel_pays = models.CharField(max_length=20, choices=USER_PAYS,default='côte_ivoire')
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
 
    is_online = models.BooleanField(default=False)  # champ pour le statut en ligne
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='personnel_set',  # Ajoutez un related_name unique
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='personnel_permissions_set',  # Ajoutez un related_name unique
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.username} -{self.Personnel_pays}"

    # Signaux pour mettre à jour le statut en ligne et la date de dernière connexion
    @receiver(user_logged_in)
    def user_logged_in_handler(sender, request, user, **kwargs):
        user.is_online = True
        user.last_login = timezone.now()  # Met à jour le champ last_login
        user.save()

    @receiver(user_logged_out)
    def user_logged_out_handler(sender, request, user, **kwargs):
        user.is_online = False
        user.save()
        
    
class VerificationCode(models.Model):
    user = models.OneToOneField(Personnel, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.code}"
class Client(SafeDeleteModel,LifecycleModel):
    _safedelete_policy=SOFT_DELETE_CASCADE
    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)

    nom = models.CharField(max_length=50)
    adresse = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return  f"{self.nom} -{self.pays}"


class Commodite(SafeDeleteModel,LifecycleModel):
    _safedelete_policy=SOFT_DELETE_CASCADE
    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=False, blank=False)
    nom_commodite = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return  f"{self.nom_commodite} -{self.pays}"
    
    


class Site(SafeDeleteModel,LifecycleModel):
    _safedelete_policy=SOFT_DELETE_CASCADE
    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    nom_site = models.CharField(max_length=50, unique=True)
    contact_site = models.CharField(max_length=20)
    lieu_site = models.CharField(max_length=150, unique=True)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=False, blank=False)
    
    def __str__(self):
        return  f"{self.nom_site} -{self.pays}"

class Site_empotage(SafeDeleteModel,LifecycleModel):
    _safedelete_policy=SOFT_DELETE_CASCADE
    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    nom_site = models.CharField(max_length=50, unique=True)
    contact_site = models.CharField(max_length=20)
    lieu_site = models.CharField(max_length=150, unique=True)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return  f"{self.nom_site} -{self.pays}"



class POD(SafeDeleteModel,LifecycleModel):
    _safedelete_policy=SOFT_DELETE_CASCADE
    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    nom_POD = models.CharField(max_length=50, unique=True)
    lieu_POD = models.CharField(max_length=150, unique=True)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return  f"{self.nom_POD} -{self.pays}"


class POL(SafeDeleteModel,LifecycleModel):
    _safedelete_policy=SOFT_DELETE_CASCADE
    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=False, blank=False)

    nom_POL = models.CharField(max_length=50, unique=True)
    lieu_POL = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return  f"{self.nom_POL} -{self.pays}"


class CompagnieMaritime(SafeDeleteModel,LifecycleModel):
    _safedelete_policy=SOFT_DELETE_CASCADE
    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    nom_compagnie_maritime = models.CharField(max_length=50, unique=True)
    lieu_compagnie_maritime = models.CharField(max_length=150, unique=True)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return  f"{self.nom_compagnie_maritime} -{self.pays}"
    
class FichierJoint(models.Model):
    fichier = models.FileField(upload_to='fichiers_joints/')
    
    def __str__(self):
        return self.fichier.name

class Dossier(SafeDeleteModel,LifecycleModel):
    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)

    _safedelete_policy=SOFT_DELETE_CASCADE
    STATUT_CHOICES= [
        ('en_attente', ' En Attente'),
        ('selection_en_cours','Selection en cours'),
        ('ACCONAGE_FAIT','empotage en cours'),
        ('Aconage_en_cours', "En Attente d'empotage"),
        ('dossier_termine', 'Termine'),
    ]
    TAILLE_CONTENEUR= [
        ('10_pieds','10 Pieds'),
        ('20_pieds','20 Pieds'),
        ('ISO_20_pieds','ISO 20 Pieds'),
        ('40_pieds','40 Pieds'),
    ]
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE)

    statut=models.CharField(max_length=25,choices=STATUT_CHOICES,default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    projet = models.CharField(max_length=50, unique=True)
    TRD = models.CharField(max_length=50)
    booking = models.CharField(max_length=50)
    type_conteneur = models.CharField(max_length=13,choices=TAILLE_CONTENEUR)
    compagnie_maritime = models.ForeignKey(CompagnieMaritime, on_delete=models.CASCADE)
    port_de_chargement = models.ForeignKey(POL, on_delete=models.CASCADE)
    port_de_dechargement = models.ForeignKey(POD, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    Site_empotage = models.ForeignKey(Site_empotage, on_delete=models.CASCADE)
    commodite = models.ForeignKey(Commodite, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    agent_selection = models.ForeignKey(Personnel, limit_choices_to={'Personnel_type': 'agent_selection'}, on_delete=models.CASCADE, related_name='dossiers_selection')
    agent_acconage = models.ForeignKey(Personnel, limit_choices_to={'Personnel_type': 'agent_acconage'}, on_delete=models.CASCADE, related_name='dossiers_acconage', null=True, blank=True)
    secretaire = models.ForeignKey(Personnel, limit_choices_to={'Personnel_type': 'secretaire'}, on_delete=models.CASCADE, null=True, blank=True)
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    fichiers = models.ManyToManyField(FichierJoint, blank=True)  
    Date_selection = models.DateTimeField("Date de sélection", blank=True, null=True)
    Date_acconage = models.DateTimeField("Date d'acconage", blank=True, null=True)
    Date_terminer = models.DateTimeField("Date de fin ", blank=True, null=True)
    def __str__(self):
        return f"Dossier {self.TRD} - {self.projet}"
    
    
    def envoyer_pour_selection(self):
        if self.statut == 'en_attente':
            self.statut = 'selection_en_cours'
            self.Date_selection = timezone.now()  # Set the selection date
            self.save()

    def finaliser_selection(self):
        if self.statut == 'selection_en_cours':
            self.statut = 'Aconage_en_cours'
            self.save()
    
    def marquer_comme_acconage_fait(self):
        # Logique pour mettre à jour l'état du dossier
        self.statut = 'ACCONAGE_FAIT'
        self.Date_acconage = timezone.now()  # Set the acconage date
        self.save()

    def terminer_dossier(self):
        self.statut = 'dossier_termine'
        self.Date_terminer = timezone.now()  # Set the completion date
        self.save()
        
    def retrograder_en_selection(self):
        """
        Change le statut du dossier en 'selection_en_cours' et envoie un e-mail à l'agent de sélection.
        """
        if self.statut in 'Aconage_en_cours' or 'ACCONAGE_FAIT':
            self.statut = 'selection_en_cours'
            self.Date_selection = timezone.now()  # Mettre à jour la date de sélection
            
            # Sauvegarder les modifications du dossier
            self.save()

            # Envoyer un e-mail à l'agent de sélection
            subject = f"Nouveau dossier à mettre à jour : {self.projet}"
            message = f"Bonjour {self.agent_selection},\n\n" \
                    f"Vous avez reçu un nouveau dossier à mettre à jour : {self.TRD} - {self.projet}.\n" \
                    "Merci de votre attention."

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # L'email de l'expéditeur
                [self.agent_selection.email],  # L'email de l'agent de sélection
                fail_silently=False,
                #cc=['ibrakdev@gmail.com','trading@oils-of-africa.ci','alice.tuo@oils-of-africa.ci', 'africa@oils-of-africa.ci','ops@oils-of-africa.ci','infos@oils-of-africa.ci','fitting.loadingassistance1@oils-of-africa.ci'],
            )

    
class Conteneur(SafeDeleteModel,LifecycleModel):

    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)

    _safedelete_policy=SOFT_DELETE_CASCADE

    TYPE_ETATS = [
        ('excellent', 'Excellent'), 
        ('moyen','Moyen'),
        ('mauvais', 'Mauvais'),
    ]
    
    STATUT_CHOICES = [
        ('Non_aconer', 'Non habillé & Non empote'),
        ('aconer', 'empote'),
    ]
    reference = models.CharField(max_length=50, unique=True)
    etat = models.CharField(max_length=10, choices=TYPE_ETATS)
    photo_devant = models.ImageField(upload_to='photos_devant/')
    photo_derriere = models.ImageField(upload_to='photos_derriere/')
    photo_interieur = models.ImageField(upload_to='photos_interieur/')
    photo_lateral_droit = models.ImageField(upload_to='photo_lateral_droit/')
    photo_lateral_gauche = models.ImageField(upload_to='photo_lateral_gauche/')
    poids_brute = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    poids_equipements = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    poids_net = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    numero_heating_pad = models.CharField(max_length=50, blank=True, null=True)
    photo_heating_pad = models.ImageField(upload_to='photos_heating_pad/', blank=True, null=True)
    numero_flexitank = models.CharField(max_length=50, blank=True, null=True)
    photo_flexitank = models.ImageField(upload_to='photos_flexitank/', blank=True, null=True)
    numero_plomb = models.CharField(max_length=50, blank=True, null=True)
    photo_plomb = models.ImageField(upload_to='photos_plomb/', blank=True, null=True)
    numero_plomb2 = models.CharField(max_length=50, blank=True, null=True)
    photo_plomb2 = models.ImageField(upload_to='photos_plomb2/', blank=True, null=True)
    numero_plomb3 = models.CharField(max_length=50, blank=True, null=True)
    photo_plomb3 = models.ImageField(upload_to='photos_plomb3/', blank=True, null=True)
    dossier = models.ForeignKey(Dossier, related_name='conteneurs',on_delete=models.CASCADE)
    agent_selection = models.ForeignKey(Personnel, limit_choices_to={'Personnel_type': 'agent_selection'}, on_delete=models.CASCADE, related_name='conteneurs_selection')
    agent_acconage = models.ForeignKey(Personnel, limit_choices_to={'Personnel_type': 'agent_acconage'}, on_delete=models.CASCADE, related_name='conteneurs_acconage', null=True, blank=True)
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='Non_aconer'
    )
    
   
    def __str__(self):
        return self.reference
    
    
    def verifier_et_changer_statut(self):
        # Liste des champs nécessaires pour qu'un conteneur soit 'Aconer'
        champs_requis = [
            
            #self.poids_equipements,
            self.poids_net,
            self.numero_plomb,
            self.photo_plomb,
        ]
        
        # Vérifier si tous les champs sont remplis (pas None)
        if all(champs_requis):
            self.statut = 'aconer'
            self.save()  # Enregistrer le changement
        else:
            self.statut = 'Non_aconer'
            self.save()  # Mettre à jour le statut en 'À compléter'
    
    def calcule_poid_brute(self):
        # Calcul automatique du poids brut si poids net et poids équipements sont fournis
        if self.poids_net is not None and self.poids_equipements is not None:
            self.poids_brute = self.poids_net + self.poids_equipements

    def save(self, *args, **kwargs):
        self.calcule_poid_brute()
        super(Conteneur, self).save(*args, **kwargs)


class Agent(SafeDeleteModel,LifecycleModel):
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=False, blank=False)

    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)

    _safedelete_policy=SOFT_DELETE_CASCADE
    
    AGENT_TYPE_CHOICES = [
        ('selection', 'Selection'),
        ('empotage', 'Empotage & Habillage '),
    ]
    Nom= models.CharField(max_length=50, unique=False)
    Prenom= models.CharField(max_length=50, unique=False)
    Agent_type = models.CharField(max_length=20, choices=AGENT_TYPE_CHOICES)

    contact = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f" {self.Nom}-{self.Prenom} {self.Agent_type} "  
    
class Dossier2(SafeDeleteModel,LifecycleModel):
    id=models.UUIDField("ID",primary_key=True,default=uuid.uuid4,editable=False)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=False, blank=False)

    _safedelete_policy=SOFT_DELETE_CASCADE
    
    TAILLE_CONTENEUR= [
        ('10_pieds','10 Pieds'),
        ('20_pieds','20 Pieds'),
        ('ISO_20_pieds','ISO 20 Pieds'),
        ('40_pieds','40 Pieds'),
    ]
    date_creation = models.DateTimeField(auto_now_add=True)
    projet = models.CharField(max_length=50, unique=True)
    TRD = models.CharField(max_length=50)
    booking = models.CharField(max_length=50)
    type_conteneur = models.CharField(max_length=13,choices=TAILLE_CONTENEUR)
    compagnie_maritime = models.ForeignKey(CompagnieMaritime, on_delete=models.CASCADE)
    port_de_chargement = models.ForeignKey(POL, on_delete=models.CASCADE)
    port_de_dechargement = models.ForeignKey(POD, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    Site_empotage = models.ForeignKey(Site_empotage, on_delete=models.CASCADE)
    commodite = models.ForeignKey(Commodite, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    agent_acconage = models.ForeignKey(Personnel, limit_choices_to={'Personnel_type': 'agent_acconage'}, on_delete=models.CASCADE, related_name='dossier2_acconages', null=True, blank=True)
   
    agent_selection =  models.ForeignKey(Personnel, limit_choices_to={'Personnel_type': 'agent_selection'}, on_delete=models.CASCADE, related_name='dossier2_selections')
    
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    date_creation = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"Dossier {self.TRD} - {self.projet}"
    
    class Meta:
        ordering = ['-date_creation']

class Document_Facture(SafeDeleteModel, LifecycleModel):
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=False, blank=False)

    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    _safedelete_policy = SOFT_DELETE_CASCADE
    dossier = models.ForeignKey(Dossier2, on_delete=models.CASCADE, related_name="factures")
    document = models.FileField(upload_to='facture/%Y/%m/%d')
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    Date_modification = models.DateTimeField(auto_now=True, editable=False)
    Date_suppression = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Archive {self.document} - Dossier {self.dossier.TRD}"

    class Meta:
        ordering = ['-Date_ajout']
        verbose_name = "Document Facture"
        verbose_name_plural = "Documents Factures"

class AutreDocument(SafeDeleteModel, LifecycleModel):
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    _safedelete_policy = SOFT_DELETE_CASCADE
    dossier = models.ForeignKey(Dossier2, on_delete=models.CASCADE, related_name="autres_documents")
    document = models.FileField(upload_to='documents/%Y/%m/%d')
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    Date_modification = models.DateTimeField(auto_now=True, editable=False)
    Date_suppression = models.DateTimeField(null=True, blank=True)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return f"Document {self.document} - Dossier {self.dossier.TRD}"

    class Meta:
        ordering = ['-Date_ajout']
        verbose_name = "Autre Document"
        verbose_name_plural = "Autres Documents"
        
class Images(SafeDeleteModel, LifecycleModel):
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    _safedelete_policy = SOFT_DELETE_CASCADE
    dossier = models.ForeignKey(Dossier2, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='images/%Y/%m/%d')
    Date_ajout = models.DateTimeField(default=timezone.now, editable=False)
    Date_modification = models.DateTimeField(auto_now=True, editable=False)
    Date_suppression = models.DateTimeField(null=True, blank=True)
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return f"Image {self.image.name} - Dossier {self.dossier.TRD}"

    class Meta:
        ordering = ['-Date_ajout']
        verbose_name = "Image"
        verbose_name_plural = "Images"


class Notification(SafeDeleteModel,LifecycleModel):
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, null=False, blank=False)

    user=models.ForeignKey(Personnel,on_delete=models.CASCADE,related_name='notification')
    message=models.TextField()
    is_read=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Notification  pour {self.user.username} - {self.message[:20]}...'