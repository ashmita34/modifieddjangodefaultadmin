from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.models import Permission,Group,User,ContentType
from django.contrib.auth.admin import UserAdmin,GroupAdmin
from django.contrib.admin import SimpleListFilter
from itertools import chain 
from.models import ServiceType
from django.utils.translation import ugettext_lazy as _
from copy import deepcopy
from django.contrib.admin import AdminSite
from django.views.decorators.cache import never_cache
from django.utils.text import capfirst
from django.template.response import TemplateResponse
from django.urls import NoReverseMatch, reverse
from django.conf.urls import url
from django.contrib.auth import models
from django.apps import apps
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class GroupListFilter(SimpleListFilter):
	title = ('group')
	parameter_name = 'group'

	def lookups(self, request, model_admin):
		items = ()
		if request.user.is_superuser:
			for group in Group.objects.all():
				items += ((str(group.id), str(group.name),),)
			return items

	def queryset(self, request, queryset):
		group_id = request.GET.get(self.parameter_name, None)
		if group_id:
			return queryset.filter(groups=group_id)
		return queryset


# class GroupRequiredMixin(object):
# 	def __init__(self, *args, **kwargs):
# 		super(GroupRequiredMixin, self).__init__(*args, **kwargs)
# 		# make user email field required
# 		self.fields['groups'].required = True




# class MyUserCreationForm(GroupRequiredMixin, UserCreationForm):
# 	pass


# class MyUserChangeForm(GroupRequiredMixin, UserChangeForm):
# 	pass

class CustomUserAdmin(UserAdmin):	
	list_filter =(GroupListFilter,)
	filter_horizontal = ('user_permissions','groups')	
	list_display=('username','email','first_name','last_name')	
	change_list_template='admin360/user/list.html'
	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		(_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
		(_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser','groups',
										'user_permissions')}),
		(_('Important dates'), {'fields': ('last_login', 'date_joined')}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('username', 'password1', 'password2','groups',),
		}),
	)
	


	def get_fieldsets(self, request, obj=None):

		fieldsets = super(UserAdmin, self).get_fieldsets(request, obj)
		if not obj:
			return self.add_fieldsets

		if not request.user.is_superuser:
			fieldsets = deepcopy(fieldsets)
			for fieldset in fieldsets:
				if 'is_superuser' in fieldset[1]['fields']:
					if type(fieldset[1]['fields']) == tuple :
						fieldset[1]['fields'] = list(fieldset[1]['fields'])
					fieldset[1]['fields'].remove('is_superuser')
					break

		return fieldsets	
			
			

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		grouptypelist=[]
		groups = request.user.groups.all()
		print(groups)
		for group in groups:
			for i in group.service_type.all():
				grouptypelist.append(i)
			
		if request.user.is_superuser:
			userlist=qs
		else:
			userlist1=qs.filter(groups__service_type__in=grouptypelist).distinct()
			notstaff=qs.filter(is_staff=False).distinct()
			userlist = userlist1 | notstaff

			
		return userlist
	
	def get_form(self, request, obj=None, **kwargs):
		# Get form from original UserAdmin.
		username = None	
		permissionslist=[]
		groupslist=[]
		
		
			
		form = super(CustomUserAdmin, self).get_form(request, obj, **kwargs)
		form.base_fields['groups'].required = True
	 
		
		if not request.user.is_superuser and request.user.is_authenticated():		

			groups = request.user.groups.all()
		
			for group in groups:
				groupslist.append(group.name)
				for i in group.permissions.all():
					permissionslist.append(i.name)
		
			user_permission=request.user.user_permissions.all()
			for i in user_permission:
				if i.name not in permissionslist:
					permissionslist.append(i.name)
			if 'user_permissions' in form.base_fields:
				permissions = form.base_fields['user_permissions']				
				permissions.queryset = permissions.queryset.filter(name__in=permissionslist)
			if 'groups' in form.base_fields:
				groups=form.base_fields['groups']
				groups.queryset=groups.queryset.filter(name__in=groupslist)
						
		return form

	# def change_view(self, request, object_id, form_url='', extra_context=None):
	# 	extra_context = extra_context or {}
	# 	extra_context['show_save_and_add_another'] = False
	# 	# or
	# 	extra_context['really_hide_save_and_add_another_damnit'] = True
	# 	return super(CustomUserAdmin, self).change_view(request, object_id,
	# 		form_url, extra_context=extra_context)


	

class CustomGroupAdmin(GroupAdmin):
	
			
	filter_horizontal = ('permissions','service_type')
	change_list_template='admin360/group/list.html'		

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		grouptypelist=[]
		groups = request.user.groups.all()

		for group in groups:
			for i in group.service_type.all():
				grouptypelist.append(i)
			
		if request.user.is_superuser:
			grouplist=qs
		else:
			grouplist=qs.filter(service_type__in=grouptypelist).distinct()
			
			
		return grouplist

	def get_form(self, request, obj=None, **kwargs):
		form = super().get_form(request, obj, **kwargs)
		
		form.base_fields['service_type'].required = True
		return form

class PermissionAdmin(admin.ModelAdmin):			
	
	change_list_template='admin360/permission/list.html'

class ServiceTypeAdmin(admin.ModelAdmin):			
	
	change_list_template='admin360/servicetype/list.html'		

	

class Admin360Site(AdminSite):
	site_header = 'VACKER 360 administration'	

	def each_context(self, request):
		context = super(Admin360Site, self).each_context(request)
		context['app_list']=self.get_app_list(request)
	
			
		models = self._registry
		perms=""
		for model, model_admin in models.items():
			app_label = model._meta.app_label

			has_module_perms = model_admin.has_module_permission(request)
			if not has_module_perms:
				continue

			perms = model_admin.get_model_perms(request)
			print(perms)
			print("permsmsm")
		if perms:
			context['has_change_permission']=perms.get('change')
			context['has_delete_permission']=perms.get('delete')
	
		return context





	





admin_site = Admin360Site(name='360admin')


admin_site.register(ServiceType,ServiceTypeAdmin)
admin_site.register(Permission,PermissionAdmin)


admin_site.register(Group,CustomGroupAdmin)
admin_site.register(User,CustomUserAdmin)
