from django.db import models
from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class ServiceType(models.Model):
	name = models.TextField(blank=True)

	def __str__(self):
		return self.name

	class Meta:
		app_label = 'auth'



Group.add_to_class('service_type', models.ManyToManyField(ServiceType,verbose_name=_('Service Type'),blank=True,))



