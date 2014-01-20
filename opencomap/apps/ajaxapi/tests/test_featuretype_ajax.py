from AjaxTest import AjaxTest
from opencomap.apps.backend.models.choice import STATUS_TYPES

class FeatureTypeAjaxTest(AjaxTest):
	def test_updateDescriptionWithCreator(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'description': 'new description'}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"description": "new description"')

	def test_updateDescriptionWithAdmin(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'description': 'newer description'}, 'george')
		self.assertContains(response, '"description": "newer description"')
		self.assertEqual(response.status_code, 200)

	def test_updateDescriptionWithContributor(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'description': 'new description'}, 'diego')
		self.assertEqual(response.status_code, 401)

	def test_updateDescriptionWithNonMember(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'description': 'new description'}, 'mehmet')
		self.assertEqual(response.status_code, 401)

	def test_updateDescriptionWrongMethod(self):
		response = self.post('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'description': 'new description'}, 'diego')
		self.assertEqual(response.status_code, 405)

	def test_updateDescriptionNonExistingFeaturetype(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/684640654540', {'description': 'new description'}, 'eric')
		self.assertEqual(response.status_code, 404)

	def test_updateFalseStatus(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'status': 656045}, 'eric')
		self.assertEqual(response.status_code, 400)

	def test_updateCorrectStatus(self):
		response = self.put('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), {'status': STATUS_TYPES['INACTIVE']}, 'eric')
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '"status": ' + str(STATUS_TYPES['INACTIVE']))

	def test_deleteWithCreator(self):
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), 'eric')
		self.assertEqual(response.status_code, 200)

	def test_deleteWithAdmin(self):
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), 'george')
		self.assertEqual(response.status_code, 200)

	def test_deleteWithContributor(self):
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), 'diego')
		self.assertEqual(response.status_code, 401)

	def test_deleteWithNonMember(self):
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/featuretypes/' + str(self.featureType.id), 'mehmet')
		self.assertEqual(response.status_code, 401)

	def test_deleteNonExistingFeaturetype(self):
		response = self.delete('/ajax/projects/' + str(self.project.id) + '/featuretypes/684640654540', 'eric')
		self.assertEqual(response.status_code, 404)