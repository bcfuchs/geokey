from django.views.generic import TemplateView, CreateView
from django.contrib import auth
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.html import strip_tags
from django.contrib.auth.views import password_reset_confirm as reset_view

from braces.views import LoginRequiredMixin

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from provider.oauth2.models import Client, AccessToken

from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)
from projects.models import Project, Admins
from projects.base import STATUS
from datagroupings.models import Grouping

from .serializers import (
    UserSerializer, UserGroupSerializer, GroupingUserGroupSerializer
)
from .models import User, GroupingUserGroup
from .forms import (
    UserRegistrationForm,
    UsergroupCreateForm,
    CustomPasswordChangeForm
)


# ############################################################################
#
# ADMIN VIEWS
#
# ############################################################################


class Index(TemplateView):
    """
    Displays the splash page. Redirects to dashboard if a user is looged in.
    """
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return self.render_to_response(self.get_context_data)
        else:
            return redirect('admin:dashboard')


class Dashboard(LoginRequiredMixin, TemplateView):
    """
    Displays the dashboard.
    """
    template_name = 'dashboard.html'

    def get_context_data(self):
        projects = Project.objects.get_list(self.request.user)

        return {
            'admin_projects': projects.filter(admins=self.request.user),
            'involved_projects': projects.exclude(admins=self.request.user),
            'status_types': STATUS
        }


class CreateUserMixin(object):
    def create_user(self, data):
        user = User.objects.create_user(
            data.get('email'),
            data.get('display_name'),
            password=data.get('password')
        )
        user.save()
        return user


class SignupAdminView(CreateUserMixin, CreateView):
    """
    Displays the sign-up page
    """
    template_name = 'users/signup.html'
    form_class = UserRegistrationForm

    def form_valid(self, form):
        """
        Registers the user if the form is valid and no other has been
        regstered with the username.
        """
        data = form.cleaned_data
        self.create_user(data)

        user = auth.authenticate(
            username=data.get('email'),
            password=data.get('password')
        )

        auth.login(self.request, user)
        return redirect('admin:dashboard')

    def form_invalid(self, form):
        """
        The form is invalid or another user has already been registerd worth
        that username. Displays the error message.
        """
        context = self.get_context_data(form=form, user_exists=True)
        return self.render_to_response(context)


class SignupAPIView(CreateUserMixin, APIView):
    def post(self, request):
        data = request.DATA
        form = UserRegistrationForm(data)
        client_id = data.pop('client_id', None)

        try:
            Client.objects.get(client_id=client_id)
            if form.is_valid():
                user = self.create_user(data)
                serializer = UserSerializer(user)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'errors': form.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Client.DoesNotExist:
            return Response(
                {'errors': {'client': 'Client ID not provided or incorrect.'}},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserGroupList(LoginRequiredMixin, TemplateView):
    template_name = 'users/usergroup_list.html'

    def get_context_data(self, project_id):
        project = Project.objects.as_admin(self.request.user, project_id)
        return super(UserGroupList, self).get_context_data(project=project)


class UserGroupCreate(LoginRequiredMixin, CreateView):
    """
    Displays the create user group page
    `/admin/projects/:project_id/usergroups/new/`
    """
    template_name = 'users/usergroup_create.html'
    form_class = UsergroupCreateForm

    @handle_exceptions_for_admin
    def get_context_data(self, **kwargs):
        """
        Creates the request context for rendering the page
        """
        project_id = self.kwargs['project_id']

        context = super(
            UserGroupCreate, self).get_context_data(**kwargs)

        context['project'] = Project.objects.as_admin(
            self.request.user, project_id
        )
        return context

    def get_success_url(self):
        """
        Returns the redirect URL that is called after the user group has been
        created.
        """
        project_id = self.kwargs['project_id']
        return reverse(
            'admin:usergroup_overview',
            kwargs={'project_id': project_id, 'group_id': self.object.id}
        )

    def form_valid(self, form):
        """
        Creates the project and redirects to the project overview page
        """
        project_id = self.kwargs['project_id']
        project = Project.objects.as_admin(self.request.user, project_id)

        form.instance.project = project
        messages.success(self.request, "The user group has been created.")
        return super(UserGroupCreate, self).form_valid(form)


class UserGroupOverview(LoginRequiredMixin, TemplateView):
    """
    Displays the user group settings page
    `/admin/projects/:project_id/usergroups/:group_id/`
    """
    template_name = 'users/usergroup_overview.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, group_id):
        """
        Creates the request context for rendering the page
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        group = project.usergroups.get(pk=group_id)

        return {'group': group, 'status_types': STATUS}


class AdministratorsOverview(LoginRequiredMixin, TemplateView):
    """
    Displays the user group settings page
    `/admin/projects/:project_id/usergroups/:group_id/`
    """
    template_name = 'users/usergroup_admins.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Creates the request context for rendering the page
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        return {'project': project}


class UserGroupSettings(LoginRequiredMixin, TemplateView):
    """
    Displays the user group settings page
    `/admin/projects/:project_id/usergroups/:group_id/settings/`
    """
    template_name = 'users/usergroup_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, group_id):
        """
        Creates the request context for rendering the page
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        group = project.usergroups.get(pk=group_id)

        return {'group': group, 'status_types': STATUS}

    def post(self, request, project_id, group_id):
        context = self.get_context_data(project_id, group_id)
        group = context.pop('group', None)

        data = request.POST

        group.name = strip_tags(data.get('name'))
        group.description = strip_tags(data.get('description'))
        group.save()

        messages.success(self.request, "The user group has been updated.")
        context['group'] = group
        return self.render_to_response(context)


class UserGroupPermissions(LoginRequiredMixin, TemplateView):
    """
    Displays the user group settings page
    `/admin/projects/:project_id/usergroups/:group_id/settings/`
    """
    template_name = 'users/usergroup_permissions.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, group_id):
        """
        Creates the request context for rendering the page
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        group = project.usergroups.get(pk=group_id)
        return super(UserGroupPermissions, self).get_context_data(group=group)


class UserGroupDelete(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, group_id):
        """
        Creates the request context for rendering the page
        """
        project = Project.objects.as_admin(self.request.user, project_id)
        group = project.usergroups.get(pk=group_id)
        return super(UserGroupDelete, self).get_context_data(group=group)

    def get(self, request, project_id, group_id):
        context = self.get_context_data(project_id, group_id)
        group = context.pop('group', None)

        if group is not None:
            group.delete()

        messages.success(self.request, 'The user group has been deleted.')
        return redirect('admin:usergroup_list', project_id=project_id)


class UserProfile(LoginRequiredMixin, TemplateView):
    """
    Displays the user profile page
    `/admin/profile`
    """
    template_name = 'users/profile.html'

    @handle_exceptions_for_admin
    def get_context_data(self, **kwargs):
        """
        Creates the request context for rendering the page
        """
        context = super(UserProfile, self).get_context_data(**kwargs)

        referer = self.request.META.get('HTTP_REFERER')
        if referer is not None and 'profile/password/change' in referer:
            context['password_reset'] = True

        return context

    def post(self, request):
        """
        Updates the user information
        """
        user = request.user

        user.email = request.POST.get('email')
        user.display_name = request.POST.get('display_name')

        user.save()

        context = self.get_context_data()
        messages.success(request, 'The user information has been updated.')
        return self.render_to_response(context)


class UserNotifications(LoginRequiredMixin, TemplateView):
    """
    Displays the notifications settings page
    `/admin/profile/notifications/`
    """
    template_name = 'users/notifications.html'

    @handle_exceptions_for_admin
    def get_context_data(self, **kwargs):
        user = self.request.user

        context = super(UserNotifications, self).get_context_data(**kwargs)
        context['admins'] = Admins.objects.filter(user=user)

        return context

    @handle_exceptions_for_admin
    def post(self, request):
        context = self.get_context_data()
        data = self.request.POST

        for project in context.get('admins'):
            new_val = data.get(str(project.project.id)) is not None

            if project.contact != new_val:
                project.contact = new_val
                project.save()

        messages.success(request, 'Notifications have been updated.')
        return self.render_to_response(context)


def password_reset_confirm(request, *args, **kwargs):
    return reset_view(
        request,
        set_password_form=CustomPasswordChangeForm,
        *args,
        **kwargs
    )


class ChangePassword(LoginRequiredMixin, TemplateView):
    """
    Displays the change password page
    `/admin/profile/password/change`
    """
    template_name = 'users/changepassword.html'

    def post(self, request):
        """
        Changes the password.
        """
        user = request.user
        user = auth.authenticate(
            username=user.email,
            password=request.POST.get('old_password')
        )

        if user is not None:
            user.set_password(request.POST.get('new_password1'))
            user.save()

            AccessToken.objects.filter(user=user).delete()

            messages.success(request, 'The password has been changed.')
            return redirect('admin:userprofile')
        else:
            messages.error(request, 'We were not able to athorise you with '
                                    'your old password. The password has not '
                                    'been changed.')
            return self.render_to_response(self.get_context_data())


# ############################################################################
#
# AJAX VIEWS
#
# ############################################################################

class QueryUsers(APIView):
    """
    AJAX endpoint for querying a list of users
    `/ajax/users/?query={username}
    """
    def get(self, request, format=None):
        q = request.GET.get('query').lower()
        users = User.objects.filter(
            display_name__icontains=q).exclude(pk=1)[:10]

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserGroup(APIView):
    """
    API Endpoints for a usergroup of a project in the AJAX API.
    /ajax/projects/:project_id/usergroups/:usergroup_id/
    """
    @handle_exceptions_for_ajax
    def put(self, request, project_id, group_id, format=None):
        """
        Updates user group information
        """
        project = Project.objects.as_admin(request.user, project_id)
        group = project.usergroups.get(pk=group_id)
        serializer = UserGroupSerializer(
            group, data=request.DATA, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, group_id, format=None):
        """
        Deletes a user group
        """
        project = Project.objects.as_admin(request.user, project_id)
        group = project.usergroups.get(pk=group_id)

        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserGroupUsers(APIView):
    """
    API Endpoints for users in a usergroup of a project in the AJAX API.
    /ajax/projects/:project_id/usergroups/:usergroup_id/users/
    """

    @handle_exceptions_for_ajax
    def post(self, request, project_id, group_id, format=None):
        """
        Adds a user to the usergroup
        """
        project = Project.objects.as_admin(request.user, project_id)
        group = project.usergroups.get(pk=group_id)

        try:
            user = User.objects.get(pk=request.DATA.get('userId'))
            group.users.add(user)

            serializer = UserGroupSerializer(group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                'The user you are trying to add to the user group does ' +
                'not exist',
                status=status.HTTP_400_BAD_REQUEST
            )


class UserGroupSingleUser(APIView):
    """
    API Endpoints for a user in a usergroup of a project in the AJAX API.
    /ajax/projects/:project_id/usergroups/:usergroup_id/users/:user_id
    """

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, group_id, user_id, format=None):
        """
        Removes a user from the user group
        """
        project = Project.objects.as_admin(request.user, project_id)
        group = project.usergroups.get(pk=group_id)

        user = group.users.get(pk=user_id)
        group.users.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserGroupViews(APIView):
    """
    AJAX API endpoint for views assigned to the user group
    `/ajax/project/:project_id/usergroups/:group_id/views/`
    """
    @handle_exceptions_for_ajax
    def post(self, request, project_id, group_id, format=None):
        """
        Assigns a new view to the user group
        """
        project = Project.objects.as_admin(request.user, project_id)
        group = project.usergroups.get(pk=group_id)

        try:
            grouping = project.groupings.get(pk=request.DATA.get('grouping'))
            view_group = GroupingUserGroup.objects.create(
                grouping=grouping,
                usergroup=group
            )
            serializer = GroupingUserGroupSerializer(
                view_group, data=request.DATA, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Grouping.DoesNotExist:
            return Response(
                'The data grouping you are trying to add to the user group is'
                'not assigned to this project.',
                status=status.HTTP_400_BAD_REQUEST
            )


class UserGroupSingleView(APIView):
    """
    AJAX API endpoint for views assigned to the user group
    `/ajax/project/:project_id/usergroups/:group_id/views/:grouping_id/`
    """
    def get_object(self, user, project_id, group_id, grouping_id):
        project = Project.objects.as_admin(user, project_id)
        group = project.usergroups.get(pk=group_id)
        return group.viewgroups.get(grouping_id=grouping_id)

    @handle_exceptions_for_ajax
    def put(self, request, project_id, group_id, grouping_id, format=None):
        """
        Updates the relation between user group and view, e.g. granting
        permissions on the view to the user group members.
        """
        view_group = self.get_object(
            request.user, project_id, group_id, grouping_id)

        serializer = GroupingUserGroupSerializer(
            view_group, data=request.DATA, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, group_id, grouping_id, format=None):
        """
        Removes the relation between usergroup and view.
        """
        view_group = self.get_object(
            request.user, project_id, group_id, grouping_id)
        view_group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ############################################################################
#
# PUBLIC API VIEWS
#
# ############################################################################

# N/A
