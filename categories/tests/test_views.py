import json

from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from projects.tests.model_factories import UserF, ProjectF
from datagroupings.models import Grouping

from .model_factories import (
    CategoryFactory, TextFieldFactory, NumericFieldFactory,
    LookupFieldFactory, LookupValueFactory, MultipleLookupFieldFactory,
    MultipleLookupValueFactory
)

from ..models import Category, Field
from ..views import (
    CategoryUpdate, FieldUpdate, FieldLookupsUpdate, FieldLookups,
    SingleCategory, CategoryCreate, CategorySettings,
    FieldCreate, CategoryList, CategoryDisplay, FieldsReorderView
)

# ############################################################################
#
# ADMIN PAGES
#
# ############################################################################


class CategoryOverviewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

    def get(self, user):
        view = CategoryList.as_view()
        url = reverse('admin:category_list', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(request, project_id=self.project.id).render()

    def test_get_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )


class CategoryCreateTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

    def get(self, user):
        view = CategoryCreate.as_view()
        url = reverse('admin:category_create', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(request, project_id=self.project.id).render()

    def post(self, user, data):
        view = CategoryCreate.as_view()
        url = reverse('admin:category_create', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.post(url, data, follow=True)

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        request.user = user
        return view(request, project_id=self.project.id)

    def test_get_create_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_create_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_create_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )

    def test_post_valid_without_grouping(self):
        data = {
            'name': 'Test',
            'description': 'Test Description',
            'default_status': 'active',
            'create_grouping': 'False'
        }
        response = self.post(self.admin, data)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(Grouping.objects.all().count(), 0)

    def test_post_valid_with_grouping(self):
        data = {
            'name': 'Test',
            'description': 'Test Description',
            'default_status': 'active',
            'create_grouping': 'True'
        }
        response = self.post(self.admin, data)
        self.assertTrue(isinstance(response, HttpResponseRedirect))
        self.assertEqual(Grouping.objects.all().count(), 1)


class CategoryDisplayTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory.create(
            **{'project': self.project}
        )

    def get(self, user):
        view = CategoryDisplay.as_view()
        url = reverse('admin:category_display', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id).render()

    def test_get_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )


class ObservationTypeSettingsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory.create(
            **{'project': self.project})

    def get(self, user):
        view = CategorySettings.as_view()
        url = reverse('admin:category_settings', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id).render()

    def test_get_settings_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_settings_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_settings_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )


class FieldCreateTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory.create(
            **{'project': self.project})

    def get(self, user):
        view = FieldCreate.as_view()
        url = reverse('admin:category_field_create', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id).render()

    def post(self, user, data):
        view = FieldCreate.as_view()
        url = reverse('admin:category_field_create', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id
        })
        request = self.factory.post(url, data)
        request.user = user

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id)

    def test_get_create_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_post_create_with_admin(self):
        data = {
            'name': 'Test name',
            'description': 'Test description',
            'required': False,
            'type': 'TextField'
        }
        response = self.post(self.admin, data)
        self.assertEquals(type(response), HttpResponseRedirect)

    def test_post_create_with_admin_and_long_name(self):
        data = {
            'name': 'Test name that is really long more than 30 chars',
            'description': 'Test description',
            'required': False,
            'type': 'TextField'
        }
        response = self.post(self.admin, data)
        self.assertEquals(type(response), HttpResponseRedirect)

    def test_get_create_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_create_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )


class FieldSettingsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.category = CategoryFactory.create(
            **{'project': self.project})
        self.field = TextFieldFactory.create(
            **{'category': self.category})

    def get(self, user):
        view = FieldCreate.as_view()
        url = reverse('admin:category_field_settings', kwargs={
            'project_id': self.project.id,
            'category_id': self.category.id,
            'field_id': self.field.id
        })
        request = self.factory.get(url)
        request.user = user
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id,
            field_id=self.field.id).render()

    def test_get_settings_with_admin(self):
        response = self.get(self.admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_settings_with_contributor(self):
        response = self.get(self.contributor)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_settings_with_non_member(self):
        response = self.get(self.non_member)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response,
            'Project matching query does not exist.'
        )

# ############################################################################
#
# AJAX API
#
# ############################################################################


class CategoryAjaxTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        self.active_type = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def _put(self, data, user):
        url = reverse(
            'ajax:category',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id
            }
        )
        request = self.factory.put(url, data)
        force_authenticate(request, user=user)
        view = CategoryUpdate.as_view()
        return view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id
        ).render()

    def test_update_not_existing_type(self):
        url = reverse(
            'ajax:category',
            kwargs={
                'project_id': self.project.id,
                'category_id': 2376
            }
        )
        request = self.factory.put(url, {'status': 'inactive'})
        force_authenticate(request, user=self.admin)
        view = CategoryUpdate.as_view()
        response = view(
            request,
            project_id=self.project.id,
            category_id=2376
        ).render()
        self.assertEqual(response.status_code, 404)

    def test_update_wrong_status(self):
        response = self._put({'status': 'bockwurst'}, self.admin)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            self.active_type.status
        )

    def test_update_description_with_admin(self):
        response = self._put({'description': 'new description'}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).description,
            'new description'
        )

    def test_update_status_with_admin(self):
        response = self._put({'status': 'inactive'}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            'inactive'
        )

    def test_update_description_with_contributor(self):
        response = self._put(
            {'description': 'new description'}, self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).description,
            self.active_type.description
        )

    def test_update_status_with_contributor(self):
        response = self._put(
            {'status': 'inactive'},
            self.contributor
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            self.active_type.status
        )

    def test_update_description_with_non_member(self):
        response = self._put(
            {'description': 'new description'},
            self.non_member
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).description,
            self.active_type.description
        )

    def test_update_status_with_contributor_non_member(self):
        response = self._put(
            {'status': 'inactive'},
            self.non_member
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            Category.objects.get_single(
                self.admin, self.project.id, self.active_type.id).status,
            self.active_type.status
        )


class ReorderFieldsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.category = CategoryFactory.create()

        self.field_0 = TextFieldFactory.create(
            **{'category': self.category})
        self.field_1 = TextFieldFactory.create(
            **{'category': self.category})
        self.field_2 = TextFieldFactory.create(
            **{'category': self.category})
        self.field_3 = TextFieldFactory.create(
            **{'category': self.category})
        self.field_4 = TextFieldFactory.create(
            **{'category': self.category})

    def test_reorder(self):
        url = reverse(
            'ajax:category_fields_reorder',
            kwargs={
                'project_id': self.category.project.id,
                'category_id': self.category.id
            }
        )

        data = [
            self.field_4.id, self.field_0.id, self.field_2.id, self.field_1.id,
            self.field_3.id
        ]

        request = self.factory.post(
            url, json.dumps({'order': data}), content_type='application/json')
        force_authenticate(request, user=self.category.project.creator)
        view = FieldsReorderView.as_view()
        response = view(
            request,
            project_id=self.category.project.id,
            category_id=self.category.id
        ).render()

        self.assertEqual(response.status_code, 200)

        fields = self.category.fields.all()

        self.assertTrue(fields.ordered)
        self.assertEqual(fields[0], self.field_4)
        self.assertEqual(fields[1], self.field_0)
        self.assertEqual(fields[2], self.field_2)
        self.assertEqual(fields[3], self.field_1)
        self.assertEqual(fields[4], self.field_3)

    def test_reorder_with_false_field(self):
        url = reverse(
            'ajax:category_fields_reorder',
            kwargs={
                'project_id': self.category.project.id,
                'category_id': self.category.id
            }
        )

        data = [
            self.field_4.id, self.field_0.id, self.field_2.id, self.field_1.id,
            655123135135
        ]

        request = self.factory.post(
            url, json.dumps({'order': data}), content_type='application/json')
        force_authenticate(request, user=self.category.project.creator)
        view = FieldsReorderView.as_view()
        response = view(
            request,
            project_id=self.category.project.id,
            category_id=self.category.id
        ).render()

        self.assertEqual(response.status_code, 400)

        fields = self.category.fields.all()

        self.assertTrue(fields.ordered)
        self.assertEqual(fields[0].order, 0)
        self.assertEqual(fields[1].order, 0)
        self.assertEqual(fields[2].order, 0)
        self.assertEqual(fields[3].order, 0)
        self.assertEqual(fields[4].order, 0)


class UpdateFieldTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        self.category = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

        self.field = TextFieldFactory(**{
            'category': self.category
        })

    def _put(self, data, user):
        url = reverse(
            'ajax:category_field',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.category.id,
                'field_id': self.field.id
            }
        )
        request = self.factory.put(url, data)
        force_authenticate(request, user=user)
        view = FieldUpdate.as_view()
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id,
            field_id=self.field.id
        ).render()

    def test_update_non_existing_field(self):
        url = reverse(
            'ajax:category_field',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.category.id,
                'field_id': 554454545
            }
        )
        request = self.factory.put(url, {'description': 'new description'})
        force_authenticate(request, user=self.admin)
        view = FieldUpdate.as_view()
        response = view(
            request,
            project_id=self.project.id,
            category_id=self.category.id,
            field_id=554454545
        ).render()
        self.assertEqual(response.status_code, 404)

    def test_update_description_with_admin(self):
        response = self._put({'description': 'new description'}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.category.id,
                self.field.id).description,
            'new description'
        )

    def test_update_required_with_admin(self):
        response = self._put({'required': True}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Field.objects.get_single(
                self.admin, self.project.id, self.category.id,
                self.field.id).required
        )

    def test_update_status_with_admin(self):
        response = self._put({'status': 'inactive'}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.category.id,
                self.field.id).status,
            'inactive'
        )

    def test_update_status_with_contributor(self):
        response = self._put({'status': 'inactive'}, self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.category.id,
                self.field.id).status,
            'active'
        )

    def test_update_status_with_non_member(self):
        response = self._put({'status': 'inactive'}, self.non_member)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.category.id,
                self.field.id).status,
            'active'
        )

    def test_update_wrong_status_with_admin(self):
        response = self._put({'status': 'bla'}, self.admin)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.category.id,
                self.field.id).status,
            'active'
        )


class UpdateNumericField(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        self.category = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

        self.field = NumericFieldFactory(**{
            'category': self.category
        })

    def _put(self, data, user):
        url = reverse(
            'ajax:category_field',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.category.id,
                'field_id': self.field.id
            }
        )
        request = self.factory.put(url, data)
        force_authenticate(request, user=user)
        view = FieldUpdate.as_view()
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id,
            field_id=self.field.id
        ).render()

    def test_update_numericfield_description_with_admin(self):
        response = self._put({'description': 'new description'}, self.admin)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Field.objects.get_single(
                self.admin, self.project.id, self.category.id,
                self.field.id).description, 'new description'
        )


class AddLookupValueTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin]
        )

        self.active_type = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def test_add_lookupvalue_with_admin(self):
        lookup_field = LookupFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id
            }
        )
        request = self.factory.post(url, {'name': 'Ms. Piggy'})
        force_authenticate(request, user=self.admin)
        view = FieldLookups.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id
        ).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(lookup_field.lookupvalues.all()), 1)

    def test_add_lookupvalue_to_not_existing_field(self):
        url = reverse(
            'ajax:category_lookupvalues',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': 32874893274
            }
        )
        request = self.factory.post(url, {'name': 'Ms. Piggy'})
        force_authenticate(request, user=self.admin)
        view = FieldLookups.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=32874893274
        ).render()
        self.assertEqual(response.status_code, 404)

    def test_add_lookupvalue_to_non_lookup(self):
        num_field = NumericFieldFactory(**{
            'category': self.active_type
        })
        url = reverse(
            'ajax:category_lookupvalues',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': num_field.id
            }
        )
        request = self.factory.post(url, {'name': 'Ms. Piggy'})
        force_authenticate(request, user=self.admin)
        view = FieldLookups.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=num_field.id
        ).render()
        self.assertEqual(response.status_code, 404)


class RemoveLookupValues(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin]
        )

        self.active_type = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def test_remove_lookupvalue_with_admin(self):
        lookup_field = LookupFieldFactory(**{
            'category': self.active_type
        })
        lookup_value = LookupValueFactory(**{
            'field': lookup_field
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            len(lookup_field.lookupvalues.filter(status='active')), 0
        )

    def test_remove_lookupvalue_from_not_existing_field(self):
        lookup_value = LookupValueFactory()

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': 45455,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=45455,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_remove_not_exisiting_lookupvalue(self):
        lookup_field = LookupFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': 65645445444
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=65645445444
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_remove_lookupvalue_from_non_lookup(self):
        num_field = NumericFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': num_field.id,
                'value_id': 65645445444
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=num_field.id,
            value_id=65645445444
        ).render()

        self.assertEqual(response.status_code, 404)


class AddMutipleLookupValueTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin]
        )

        self.active_type = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def test_add_lookupvalue_with_admin(self):
        lookup_field = MultipleLookupFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id
            }
        )
        request = self.factory.post(url, {'name': 'Ms. Piggy'})
        force_authenticate(request, user=self.admin)
        view = FieldLookups.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id
        ).render()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(lookup_field.lookupvalues.all()), 1)


class RemoveMultipleLookupValues(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin]
        )

        self.active_type = CategoryFactory(**{
            'project': self.project,
            'status': 'active'
        })

    def test_remove_lookupvalue_with_admin(self):
        lookup_field = MultipleLookupFieldFactory(**{
            'category': self.active_type
        })
        lookup_value = MultipleLookupValueFactory(**{
            'field': lookup_field
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            len(lookup_field.lookupvalues.filter(status='active')), 0
        )

    def test_remove_lookupvalue_from_not_existing_field(self):
        lookup_value = MultipleLookupValueFactory.create()

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': 45455,
                'value_id': lookup_value.id
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=45455,
            value_id=lookup_value.id
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_remove_not_exisiting_lookupvalue(self):
        lookup_field = MultipleLookupFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': lookup_field.id,
                'value_id': 65645445444
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=lookup_field.id,
            value_id=65645445444
        ).render()

        self.assertEqual(response.status_code, 404)

    def test_remove_lookupvalue_from_non_lookup(self):
        num_field = NumericFieldFactory(**{
            'category': self.active_type
        })

        url = reverse(
            'ajax:category_lookupvalues_detail',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.active_type.id,
                'field_id': num_field.id,
                'value_id': 65645445444
            }
        )
        request = self.factory.delete(url)
        force_authenticate(request, user=self.admin)
        view = FieldLookupsUpdate.as_view()

        response = view(
            request,
            project_id=self.project.id,
            category_id=self.active_type.id,
            field_id=num_field.id,
            value_id=65645445444
        ).render()

        self.assertEqual(response.status_code, 404)


# ############################################################################
#
# PUBLIC API
#
# ############################################################################

class ObservationTypePublicApiTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()
        self.view_member = UserF.create()

        self.project = ProjectF.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor],
            add_viewers=[self.view_member]
        )
        self.category = CategoryFactory(**{
            'status': 'active',
            'project': self.project
        })
        TextFieldFactory.create(**{
            'key': 'key_1',
            'category': self.category
        })
        NumericFieldFactory.create(**{
            'key': 'key_2',
            'category': self.category
        })
        self.inactive_field = TextFieldFactory.create(**{
            'key': 'key_3',
            'category': self.category,
            'status': 'inactive'
        })
        lookup_field = LookupFieldFactory(**{
            'key': 'key_4',
            'category': self.category
        })
        LookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': lookup_field
        })
        LookupValueFactory(**{
            'name': 'Kermit',
            'field': lookup_field
        })
        LookupValueFactory(**{
            'name': 'Gonzo',
            'field': lookup_field,
            'status': 'inactive'
        })

    def _get(self, user):
        url = reverse(
            'api:category',
            kwargs={
                'project_id': self.project.id,
                'category_id': self.category.id
            }
        )
        request = self.factory.get(url)
        force_authenticate(request, user=user)
        view = SingleCategory.as_view()
        return view(
            request,
            project_id=self.project.id,
            category_id=self.category.id
        ).render()

    def test_get_observationType_with_admin(self):
        response = self._get(self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Gonzo")
        self.assertNotContains(response, self.inactive_field.name)

    def test_get_observationType_with_contributor(self):
        response = self._get(self.contributor)
        self.assertEqual(response.status_code, 200)

    def test_get_observationType_with_view_member(self):
        response = self._get(self.view_member)
        self.assertEqual(response.status_code, 200)

    def test_get_observationType_with_non_member(self):
        response = self._get(self.non_member)
        self.assertEqual(response.status_code, 404)
