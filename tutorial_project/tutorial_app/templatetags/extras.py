from django import template

from tutorial_app.models import Category

register = template.Library()

#Create registry of custom work

@register.inclusion_tag('cat.html')
def get_category_list(cat=None):
	return {'cats':Category.objects.all(), 'act_cat':cat}