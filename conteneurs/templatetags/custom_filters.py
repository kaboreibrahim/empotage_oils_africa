import os
from django import template

register = template.Library()

@register.filter
def basename(value):
    """Retourne le nom du fichier à partir d'un chemin"""
    return os.path.basename(value)

 