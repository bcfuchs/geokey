from django.test import TestCase

from nose.tools import raises

from .model_factories import ApplicationFactory

from ..models import Application


class ApplicationModelTest(TestCase):
    @raises(Application.DoesNotExist)
    def test_delete_app(self):
        app = ApplicationFactory()
        app.delete()
        Application.objects.get(pk=app.id)

    def test_update(self):
        app = ApplicationFactory()
        app.download_url = 'http://example.com'
        app.save()

        self.assertEqual(app.download_url, 'http://example.com')
        self.assertEqual(app.client.url, 'http://example.com')
