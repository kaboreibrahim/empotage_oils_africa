import random
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from crispy_forms.bootstrap import PrependedText
from django.core.mail import send_mail
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import modelformset_factory
from django import forms

from .models import *
from django.forms import  DateTimeInput

#formulaire de connexion
class LoginForm(AuthenticationForm): 
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur ou e-mail', 'id': 'username'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe', 'id': 'password'})
    )

#formualaire de verification
class VerificationForm(forms.Form):
 
    code = forms.CharField(max_length=6)
    


#formualire de creation de compte 
class  PersonnelForm(UserCreationForm):
    class Meta:
        model = Personnel
        fields = ('first_name','last_name','photos', 'email','Contact','username','Personnel_type','password1', 'password2')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Personnel.objects.filter(email=email).exists():
            raise ValidationError("Un compte avec cet e-mail existe déjà.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Désactiver le compte jusqu'à la vérification
        if commit:
            user.save()
            code = str(random.randint(100000, 999999))
            VerificationCode.objects.create(user=user, code=code)
            send_mail(
                'Votre code de vérification',
                f'Votre code de vérification est {code}',
                'kaboremessi@gmail.com',
                [user.email],
                fail_silently=False,
            )
        return user
    
# form de site 
class SiteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Enregistrer'))
    
    class Meta:
        model=Site
        fields='__all__'
        labels={'nom_site':'Nom du Site '}


# form de site 
class SiteempotageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SiteempotageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Enregistrer'))
    
    class Meta:
        model=Site_empotage
        fields='__all__'
        labels={'nom_site':'Nom du Site '}

# form de commodite
class CommoditeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommoditeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Enregistrer'))
    class Meta :
        model=Commodite
        fields='__all__'

#orm de Port De Dechargement 
class PODForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(PODForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Enregistrer'))
    class Meta:
        model=POD
        fields='__all__'
        labels={'nom_POD':'Nom du Port de Dechagement'}



class POLForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(POLForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Enregistrer'))
    class Meta:
        model=POL
        fields='__all__'
        labels={'nom_POL':'Nom du Port de chagement'}
        
        
class CompagnieMaritimeForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(CompagnieMaritimeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Enregistrer'))
    class Meta:
        model=CompagnieMaritime
        fields='__all__'
        



class ClientForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Enregistrer'))
    class Meta:
        model=Client
        fields='__all__'
        

class DossiersForm(forms.ModelForm):
    
    """
    Formulaire pour la création et la modification des dossiers.
    """
    
    def __init__(self, *args, **kwargs):
        super(DossiersForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Enregistrer'))
        self.fields['compagnie_maritime'].queryset = CompagnieMaritime.objects.filter(pays__nom='Côte d\'Ivoire')
        self.fields['client'].queryset = Client.objects.filter(pays__nom='Côte d\'Ivoire')
        self.fields['port_de_chargement'].queryset = POL.objects.filter(pays__nom='Côte d\'Ivoire')
        self.fields['commodite'].queryset = Commodite.objects.filter(pays__nom='Côte d\'Ivoire')
        self.fields['port_de_dechargement'].queryset = POD.objects.filter(pays__nom='Côte d\'Ivoire')
        self.fields['site'].queryset = Site.objects.filter(pays__nom='Côte d\'Ivoire')
        self.fields['Site_empotage'].queryset = Site_empotage.objects.filter(pays__nom='Côte d\'Ivoire')
        self.fields['agent_selection'].queryset = Personnel.objects.filter(Personnel_pays='côte_ivoire',Personnel_type='agent_selection')
        self.fields['agent_acconage'].queryset = Personnel.objects.filter(Personnel_pays='côte_ivoire',Personnel_type='agent_acconage')
        
       
    class Meta:
        model=Dossier
        fields = ['projet', 'TRD', 'booking', 'type_conteneur', 'client', 'commodite', 'port_de_chargement', 'port_de_dechargement', 'compagnie_maritime', 'site', 'agent_selection', 'agent_acconage','Site_empotage']
       
class BaseDossierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        country = kwargs.pop('country')
        super(BaseDossierForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Enregistrer'))
        self.fields['compagnie_maritime'].queryset = CompagnieMaritime.objects.filter(pays__nom=country)
        self.fields['client'].queryset = Client.objects.filter(pays__nom=country)
        self.fields['port_de_chargement'].queryset = POL.objects.filter(pays__nom=country)
        self.fields['commodite'].queryset = Commodite.objects.filter(pays__nom=country)
        self.fields['port_de_dechargement'].queryset = POD.objects.filter(pays__nom=country)
        self.fields['site'].queryset = Site.objects.filter(pays__nom=country)
        self.fields['Site_empotage'].queryset = Site_empotage.objects.filter(pays__nom=country)
        self.fields['agent_selection'].queryset = Personnel.objects.filter(Personnel_pays=country, Personnel_type='agent_selection')
        self.fields['agent_acconage'].queryset = Personnel.objects.filter(Personnel_pays=country, Personnel_type='agent_acconage')
        self.initial['pays'] = Pays.objects.get(nom=country)

    class Meta:
        model = Dossier
        fields = ['projet', 'TRD', 'booking', 'type_conteneur', 'client', 'commodite', 'port_de_chargement', 'port_de_dechargement', 'compagnie_maritime', 'site', 'agent_selection', 'agent_acconage', 'Site_empotage']

class DossiersGabonForm(BaseDossierForm):
    """
    Un formulaire pour gérer les dossiers spécifiques au Gabon.

    Ce formulaire hérite de BaseDossierForm et définit le pays par défaut sur 'Gabon'.

    Méthodes:
        __init__(*args, **kwargs): Initialise le formulaire avec 'Gabon' comme pays.
    """
    def __init__(self, *args, **kwargs):
        kwargs['country'] = 'Gabon'
        super(DossiersGabonForm, self).__init__(*args, **kwargs)
        


class DossiersNigeriaForm(BaseDossierForm):
    def __init__(self, *args, **kwargs):
        kwargs['country'] = 'Nigeria'
        super(DossiersNigeriaForm, self).__init__(*args, **kwargs)      


        
class ConteneurForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ConteneurForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('reference', css_class='form-group col-md-6 mb-0'),
                Column('etat', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('photo_devant', css_class='form-group col-md-4 mb-0'),
                Column('photo_lateral_droit', css_class='form-group col-md-4 mb-0'),
                Column('photo_derriere', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('photo_lateral_gauche', css_class='form-group col-md-6 mb-0'),
                Column('photo_interieur', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Enregistrer')
        )

    class Meta:
        model = Conteneur
        fields = ['reference', 'etat', 'photo_devant', 'photo_derriere', 'photo_interieur','photo_lateral_droit','photo_lateral_gauche']
        
# Créez un FormSet pour le modèle Conteneur
ConteneurFormSet = modelformset_factory(
    Conteneur,
    form=ConteneurForm,
    extra=1,  # Nombre de formulaires supplémentaires à afficher
    can_delete=True
)


class ConteneurAcconageForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ConteneurAcconageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            # Poids brute et Poids équipements sur la même ligne
            Row(
                Column('poids_brute', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                Column('poids_equipements', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                css_class='form-row'
            ),
            # Poids net sur une ligne à part entière
            Row(
                Column('poids_net', css_class='form-group col-md-12 mb-0'),  # Pleine largeur
                css_class='form-row'
            ),
            # Numéro Heating Pad et Photo Heating Pad sur la même ligne
            Row(
                Column('numero_heating_pad', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                Column('photo_heating_pad', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                css_class='form-row'
            ),
            # Numéro Flexitank et Photo Flexitank sur la même ligne
            Row(
                Column('numero_flexitank', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                Column('photo_flexitank', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                css_class='form-row'
            ),
            # Numéro Plomb et Photo Plomb sur la même ligne
            Row(
                Column('numero_plomb', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                Column('photo_plomb', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                css_class='form-row'
            ),
            # Numéro Plomb et Photo Plomb sur la même ligne
            Row(
                Column('numero_plomb4', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                Column('photo_plomb4', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                css_class='form-row'
            ),
            # Numéro Plomb et Photo Plomb sur la même ligne
            Row(
                Column('numero_plomb5', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                Column('photo_plomb5', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                css_class='form-row'
            ),
            # Bouton de soumission
            
            # Bouton de soumission
            Submit('submit', 'Enregistrer')
        )

    def clean(self):
        cleaned_data = super().clean()
        poids_brute = cleaned_data.get('poids_brute')
        poids_net = cleaned_data.get('poids_net')

        if poids_net and poids_brute and poids_net > poids_brute:
            raise forms.ValidationError("Le poids net ne peut pas être supérieur au poids brut.")

        return cleaned_data

    class Meta:
        model = Conteneur
        fields = [  'poids_net', 'poids_equipements', 'numero_heating_pad', 'photo_heating_pad', 
                'numero_flexitank', 'photo_flexitank', 'numero_plomb', 'photo_plomb', 'numero_plomb4','photo_plomb4', 'numero_plomb5','photo_plomb5']


class ConteneurISO20Form(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ConteneurISO20Form, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            # Poids brute et Poids équipements sur la même ligne
            Row(
                Column('poids_brute', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                css_class='form-row'
            ),
            # Poids net sur une ligne à part entière
            Row(
                Column('poids_net', css_class='form-group col-md-12 mb-0'),  # Pleine largeur
                css_class='form-row'
            ),
               Row(
                Column('numero_plomb', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                Column('photo_plomb', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                css_class='form-row'
            ),
                Row(
                Column('numero_plomb2', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                Column('photo_plomb2', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                css_class='form-row'
            ),
                Row(
                Column('numero_plomb3', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                Column('photo_plomb3', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                css_class='form-row'
            ),
                Row(
                    Column('numero_plomb4', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                    Column('photo_plomb4', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                    css_class='form-row'
                ),
                Row(
                    Column('numero_plomb5', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                    Column('photo_plomb5', css_class='form-group col-md-6 mb-0'),  # 50% de la largeur
                    css_class='form-row'
                ),
                
            
            # Bouton de soumission
            Submit('submit', 'Enregistrer')
        )

    def clean(self):
        cleaned_data = super().clean()
        poids_brute = cleaned_data.get('poids_brute')
        poids_net = cleaned_data.get('poids_net',)

        if poids_net and poids_brute and poids_net > poids_brute:
            raise forms.ValidationError("Le poids net ne peut pas être supérieur au poids brut.")

        return cleaned_data

    class Meta:
        model = Conteneur
        fields = [  'poids_net','numero_plomb','photo_plomb','numero_plomb2','photo_plomb2','numero_plomb3','photo_plomb3','numero_plomb4','photo_plomb4','numero_plomb5','photo_plomb5']



class Dossiers2Form(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(Dossiers2Form, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Enregistrer'))
       
    class Meta:
        model=Dossier2
        fields = ['projet', 'TRD', 'booking', 'type_conteneur', 'client', 'commodite', 'port_de_chargement', 'port_de_dechargement', 'compagnie_maritime', 'site', 'agent_selection', 'agent_acconage','Site_empotage','date_creation']
       
     

 
class AgentForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(AgentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Enregistrer'))
    class Meta:
        model=Agent
        fields='__all__'
        


class DocumentFactureForm(forms.ModelForm):
    class Meta:
        model = Document_Facture
        fields = ['document']
        

class AutreDocumentForm(forms.ModelForm):
    class Meta:
        model = AutreDocument
        fields = ['document']
        
        
class ImagesForm(forms.ModelForm):
    class Meta:
        model = Images
        fields = ['image']
       