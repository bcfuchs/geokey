from django.db import models

from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings

from opencomap.apps.backend.models.choice import STATUS_TYPES
from opencomap.apps.backend.models.usergroup import UserGroup
from opencomap.apps.backend.decorators import check_status

class Project(models.Model):
	"""
	Stores a single project. Extends `Authenticatable`.
	"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(null=True)
	isprivate = models.BooleanField(default=False)
	everyonecontributes = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	creator = models.ForeignKey(settings.AUTH_USER_MODEL)
	status = models.IntegerField(default=STATUS_TYPES['ACTIVE'])
	admins = models.OneToOneField(UserGroup, related_name='admingroup')
	contributors = models.OneToOneField(UserGroup, related_name='contributorgroup')

	class Meta: 
		app_label = 'backend'

	def __unicode__(self):
		return self.name + ', ' + self.description

	@check_status
	def update(self, name=None, description=None, status=None, isprivate=None):
		"""
		Updates a project. Checks if the status is of ACTIVE or INACTIVE otherwise raises ValidationError.
		"""

		if (name): self.name = name
		if (description): self.description = description
		if (status): self.status = status
		if (isprivate != None): 
			self.isprivate = isprivate

		self.save()

	def delete(self):
		"""
		Removes the project from the listing of all projects by setting its status to `DELETED`.
		"""
		self.status = STATUS_TYPES['DELETED']
		self.save()

	def getFeatures(self):
		"""
		Returns a list of all features assinged to the project. Excludes those having status `RETIRED` and `DELETED`
		"""
		return self.feature_set.exclude(status=STATUS_TYPES['DELETED'])

	def addFeature(self, feature):
		"""
		Adds a feature to the project.

		:feature: The features to be added.
		"""
		feature.save()
		feature.projects.add(self)
		
	def removeFeatures(self, *features):
		"""
		Removes an arbitrary number of `Features`s from the `Project`.

		:feature: The feature to be removed.
		"""
		for feature in features:
			feature.projects.remove(self)
			feature.save()

	def getFeatureTypes(self):
		"""
		Returns all `FeatureTypes` assigned to the project
		"""
		return self.featuretype_set.exclude(status=STATUS_TYPES['DELETED'])

	def addFeatureType(self, featuretype):
		"""
		Adds a `FeatureType` to the project
		"""
		featuretype.project = self
		featuretype.save()


	def addView(self, view):
		"""
		Adds a `View` to the `Project`
		"""
		view.save()
		view.projects.add(self)

	def removeViews(self, *views):
		"""
		Removes an arbitraty number of `View`s from the `Project`
		"""
		for view in views:
			view.projects.remove(view)