from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Button, HTML
from django.db.models import Q
from django.contrib.auth.models import User, Group
from .models import Employee
from custom.models import *

class MunicipalityForm(forms.ModelForm):
	class Meta:
		model = Municipality
		fields = ['name']

class AdministrativePostForm(forms.ModelForm):
	class Meta:
		model = AdministrativePost
		fields = ['name']

class VillageForm(forms.ModelForm):
	class Meta:
		model = Village
		fields = ['name']