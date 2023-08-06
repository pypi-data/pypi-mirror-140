from django.db import models


class Municipality(models.Model):
	code = models.CharField(max_length=5, null=True, blank = True)
	name = models.CharField(max_length=100)
	hckey = models.CharField(max_length=10, null=True ,  blank = True)
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

	class Meta:
		verbose_name_plural = 'Dadus Custom Ba Munisipiu'

class AdministrativePost(models.Model):
	municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE, null=True)
	name = models.CharField(max_length=100)
	def __str__(self):
		template = '{0.name}'
		return template.format(self)
	class Meta:
		verbose_name_plural = 'Dadus Custom Ba Postu Administrativu'

class Village(models.Model):
	administrativepost = models.ForeignKey(AdministrativePost, on_delete=models.CASCADE, null=True)
	name = models.CharField(max_length=100)
	def __str__(self):
		template = '{0.name}'
		return template.format(self)

	class Meta:
		verbose_name_plural = 'Dadus Custom Ba Suku'

class Aldeia(models.Model):
	village = models.ForeignKey(Village, on_delete=models.CASCADE, null=True)
	name = models.CharField(max_length=100)
	def __str__(self):
		template = '{0.name}'
		return template.format(self)
	class Meta:
		verbose_name_plural = 'Dadus Custom Ba Aldeia'

class Year(models.Model):
	year = models.IntegerField()
	active = models.BooleanField(default=False)
	def __str__(self):
		template = '{0.year}'
		return template.format(self)
	class Meta:

		verbose_name_plural = 'Dadus Custom Ba Tinan'


