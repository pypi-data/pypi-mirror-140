from django.conf import settings
from django.db import models
from djangoldp.models import Model

from djangoldp.permissions import LDPPermissions
from djangoldp.utils import is_anonymous_user

from djangoldp_hiphopcommunity.permissions import *
from djangoldp_hiphopcommunity.filters import *


class Member(Model):
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="Nom")
    picture = models.ImageField(blank=True, null=True, verbose_name="Photo")
    title = models.CharField(blank=True, null=True, max_length=25, verbose_name="métier")
    society = models.CharField(blank=True, null=True, max_length=50, verbose_name="société")

    def __str__(self):
        return self.name

class Partnertype(Model):
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="Type de partenariat")

    def __str__(self):
        return self.name

class Partner(Model):
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="Nom du partenaire")
    illustration = models.ImageField(blank=True, null=True, verbose_name="illustration")
    logo = models.ImageField(blank=True, null=True, verbose_name="logo")
    partnertype = models.ForeignKey(Partnertype, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="type de partenaire")
    presentation = models.CharField(max_length=100, blank=True, null=True, verbose_name="courte présentation du partenaire" )
    offer = models.CharField(max_length=100, blank=True, null=True, verbose_name="présentation de l'offre")
    offerlink = models.URLField(blank=True, null=True, verbose_name="Lien vers l'offre")

    def __str__(self):
        return self.name

class Expert(Model):
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="Nom")
    picture = models.ImageField(blank=True, null=True, verbose_name="Photo")
    title = models.CharField(blank=True, null=True, max_length=25, verbose_name="métier")
    society = models.CharField(blank=True, null=True, max_length=50, verbose_name="société")
    contact=models.IntegerField(blank=True, null=True, verbose_name="Numéro de téléphone", help_text='Mettre le numéro au format international, sans le "+", de type "33612345678"')

    def __str__(self):
        return self.name

class Accountmanager(Model):
    name = models.CharField(max_length=25, blank=True, null=True, verbose_name="Nom")
    picture = models.ImageField(blank=True, null=True, verbose_name="Photo")
    title = models.CharField(blank=True, null=True, max_length=25, verbose_name="métier")
    contact=models.IntegerField(blank=True, null=True, verbose_name="Illustration du projet", help_text='Mettre le numéro au format international, sans le "+", de type "33612345678"')

    def __str__(self):
        return self.name

class Project(Model):
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nom du projet")
    img = models.ImageField(blank=True, null=True, verbose_name="Illustration du projet")
    presentation = models.CharField(max_length=250, blank=True, null=True, verbose_name="Présentation du projet" )
    visible = models.BooleanField(verbose_name="Visible sur le site", blank=True, null=True,  default=False)

    def __str__(self):
        return self.name

class Campain(Model):
    name= models.CharField(max_length=50, blank=True, null=True, verbose_name="nom de la campagne")
    plan = models.URLField(blank=True, null=True, verbose_name="Plan d'action")
    planning = models.URLField(blank=True, null=True, verbose_name="Planning")
    results = models.URLField(blank=True, null=True, verbose_name="Résultats")
    
    class Meta(Model.Meta):
        permission_classes = [ ToolandCampainPermissions]
        
    def __str__(self):
        return str(self.name)

class Tool(Model):
    name= models.CharField(max_length=50, blank=True, null=True, verbose_name="nom des outils")
    files = models.URLField(blank=True, null=True, verbose_name="Fichiers")
    invoice = models.URLField(blank=True, null=True, verbose_name="Factures et devis")
    
    class Meta(Model.Meta):
        permission_classes = [ ToolandCampainPermissions]
        
    def __str__(self):
        return str(self.name)

class Projectmember(Model):
    name= models.CharField(max_length=50, blank=True, null=True, verbose_name="nom du projet")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="utilisateur premium", related_name="projectmembers")
    campain = models.ForeignKey(Campain, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="campagne du projet")
    tool = models.ForeignKey(Tool, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Outils du projet")
    expert = models.ManyToManyField(Expert, blank=True, max_length=50, verbose_name="expert membre de l'équipe projet")
    account = models.ManyToManyField(Accountmanager, blank=True, max_length=50, verbose_name="Account manager")
   
    class Meta(Model.Meta):
        permission_classes = [ProjectmemberPermissions]

    def __str__(self):
        return "%s - %s" % (self.user , self.name)
