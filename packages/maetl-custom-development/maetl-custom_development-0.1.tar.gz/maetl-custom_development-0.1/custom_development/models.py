from django.db import models
from custom.models import *

# Create your models here.
class National(models.Model):
	name = models.CharField(max_length=200, null=True, verbose_name="Nasional")
	code = models.CharField(max_length=10, null=True, blank=True)
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

	class Meta:
		verbose_name_plural='Dadus Custom Ba Nasional'

class ONG(models.Model):
	name = models.CharField(max_length=30, null=True,verbose_name="ONG")

	def __str__(self):
		template = '{0.name}'
		return template.format(self)
	class Meta:
		verbose_name_plural='Dadus Custom Ba ONG'

class Agency(models.Model):
	name = models.CharField(max_length=30, null=True, verbose_name="Ajénsia")

	def __str__(self):
		template = '{0.name}'
		return template.format(self)

	class Meta:
		verbose_name_plural='Dadus Custom Ba Ajénsia'

class Company(models.Model):
	name = models.CharField(max_length=300, null=True)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural=' Dadus Custom Ba Kompañia' 

