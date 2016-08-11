from django.contrib.contenttypes.models import ContentType
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse

from dewey.views import SortMixin, FilterMixin
from ..models import Environment, Host, Role, Safe, SafeAccessControl, Secret, Vault
from ..forms import AddSecretForm, CreateSecretForm, HostSafeAccessForm, RoleSafeAccessForm, SafeUpdateForm, UpdateSecretForm, SafeCreateForm

import logging

logger = logging.getLogger('.'.join(['dewey', __name__]))


class HostListView(SortMixin, ListView):
    model = Host
    default_sort_params = ('hostname', 'asc')

    def get_template_names(self):
        return [self.kwargs['template']]

    def sort_queryset(self, queryset, order_by, order):
        if not order_by or order_by == 'hostname':
            queryset = queryset.order_by('hostname')
        if order == 'desc':
            queryset = queryset.reverse()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(HostListView, self).get_context_data(*args, **kwargs)
        context.update({'environments': Environment.objects.order_by('name')})
        context.update({'host_count': Host.objects.all().count()})
        context.update({'roles': Role.objects.order_by('name')})
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super(HostListView, self).get_queryset(*args, **kwargs)
        if 'environment' in self.request.GET.keys():
            environment = self.request.GET.get('environment')
            if environment != 'all':
                queryset = queryset.filter(environment__name=environment)
        if 'roles' in self.request.GET.keys():
            if self.request.GET.get('roles') != 'any':
                roles = self.request.GET.get('roles').split(':')
                role_list = []
                for role in roles:
                    try:
                        role_list.append(Role.objects.get(name=role))
                    except Role.DoesNotExist:
                        pass
                queryset = queryset.filter(roles__in=role_list).distinct()
        return queryset


class HostDetailView(DetailView):
    model = Host
    template_name = 'environments/host_detail.html'

    def get_object(self):
        return get_object_or_404(Host, hostname=self.kwargs['hostname'])


class SafeSecretMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super(SafeSecretMixin, self).get_context_data(*args, **kwargs)
        context.update({'secrets_count': Secret.objects.count()})
        context.update({'safes_count': Safe.objects.count()})
        return context


class SecretListView(SafeSecretMixin, ListView):
    model = Secret
    template_name = 'environments/secrets.html'

    def get_context_data(self, *args, **kwargs):
        context = super(SecretListView, self).get_context_data(*args, **kwargs)
        context.update({'secret_create_form': CreateSecretForm})
        return context


class SecretDetailView(SafeSecretMixin, DetailView):
    model = Secret
    template_name = 'environments/secret_detail.html'

    def get_object(self, queryset=None):
        safe = get_object_or_404(Safe, name=self.kwargs['safe'])
        return get_object_or_404(Secret, name=self.kwargs['name'], safe=safe)

    def get_context_data(self, *args, **kwargs):
        context = super(SecretDetailView, self).get_context_data(*args, **kwargs)
        form = UpdateSecretForm(initial={'name': self.object.name, 'secret': self.object.secret})
        context.update({'secret_form': form})
        context.update({'secret_create_form': CreateSecretForm})
        return context


class SafeListView(SafeSecretMixin, ListView):
    model = Safe
    template_name = 'environments/safes.html'

    def get_context_data(self, *args, **kwargs):
        context = super(SafeListView, self).get_context_data(*args, **kwargs)
        context.update({'safe_create_form': SafeCreateForm})
        return context


class SafeDetailView(SafeSecretMixin, DetailView):
    model = Safe
    template_name = 'environments/safe_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Safe, name=self.kwargs['name'])

    def get_context_data(self, *args, **kwargs):
        context = super(SafeDetailView, self).get_context_data(*args, **kwargs)
        context.update({'host_access_form': HostSafeAccessForm(initial={'safe': self.object.id})})
        context.update({'role_access_form': RoleSafeAccessForm(initial={'safe': self.object.id})})
        context.update({'safe_update_form': SafeUpdateForm(initial={'name': self.object.name})})
        safe_create_form = SafeCreateForm()
        safe_create_form.helper.form_action = 'safe_list'
        context.update({'safe_create_form': safe_create_form})
        context.update({'secret_form': AddSecretForm(initial={'safe': self.object.id})})
        return context


def create_secret(request, *args, **kwargs):
    form = CreateSecretForm(request.POST)
    if form.is_valid():
        secret = form.save(commit=False)
        secret.safe = get_object_or_404(Safe, id=form.cleaned_data['safe'])
        secret.save()
        messages.add_message(request, messages.SUCCESS, 'saved secret {} to {}'.format(form.cleaned_data['name'], secret.safe.name))
        return redirect('secrets')


def update_secret(request, *args, **kwargs):
    safe = get_object_or_404(Safe, name=kwargs['safe'])
    secret = get_object_or_404(Secret, name=kwargs['name'], safe=safe)
    form = UpdateSecretForm(request.POST, instance=secret)
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, 'updated secret {}'.format(secret.name))
        return redirect(reverse('secret_detail', kwargs={'name': secret.name, 'safe': safe.name}))


def delete_secret(request, *args, **kwargs):
    safe = get_object_or_404(Safe, name=request.POST.get('safe'))
    secret = get_object_or_404(Secret, name=request.POST.get('secret'), safe=safe)
    secret.delete()
    messages.add_message(request, messages.SUCCESS, 'deleted secret {} from {}'.format(secret.name, safe.name))
    return redirect(reverse('secrets'))


def secrets(request, *args, **kwargs):
    if request.method == 'GET':
        return SecretListView.as_view()(request, *args, **kwargs)
    if request.method == 'POST':
        return create_secret(request, *args, **kwargs)


def secret(request, *args, **kwargs):
    if request.method == 'GET':
        return SecretDetailView.as_view()(request, *args, **kwargs)
    if request.method == 'POST':
        if request.POST.get('verb') == 'update':
            return update_secret(request, *args, **kwargs)
        elif request.POST.get('verb') == 'delete':
            return delete_secret(request, *args, **kwargs)


def safe_list(request, *args, **kwargs):
    if request.method == 'GET':
        return SafeListView.as_view()(request, *args, **kwargs)
    elif request.method == 'POST':
        return safe_create(request, *args, **kwargs)


def safe_create(request, *args, **kwargs):
    form = SafeCreateForm(request.POST)
    if form.is_valid():
        safe = form.save(commit=False)
        vault = get_object_or_404(Vault, id=form.cleaned_data['vault'])
        safe.vault = vault
        safe.save()
        messages.add_message(request, messages.SUCCESS, 'added safe {}'.format(safe.name))
        return redirect('safe_list')


def safe_update(request, *args, **kwargs):
    safe = get_object_or_404(Safe, name=kwargs['name'])
    form = SafeUpdateForm(request.POST, instance=safe)
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, 'successfully updated {}'.format(safe.name))
        return redirect(reverse('safe_detail', kwargs={'name': safe.name}))
    messages.add_message(request, messages.ERROR, 'something went wrong saving the safe')
    return redirect(reverse('safe_list'))


def safe_delete(request, *args, **kwargs):
    safe = get_object_or_404(Safe, name=kwargs['name'])
    safe.delete()
    messages.add_message(request, messages.SUCCESS, 'successfully deleted safe {}'.format(safe.name))
    return redirect('safe_list')


def safe_details(request, *args, **kwargs):
    if request.method == 'GET':
        return SafeDetailView.as_view()(request, *args, **kwargs)
    elif request.method == 'POST':
        if request.POST.get('verb') == 'delete':
            return safe_delete(request, *args, **kwargs)
        if request.POST.get('verb') == 'update':
            return safe_update(request, *args, **kwargs)
        return redirect(reverse('safe_detail', kwargs={'name': kwargs['name']}))


def delete_safe_access(request, *args, **kwargs):
    if request.method == 'POST':
        safe = get_object_or_404(Safe, id=request.POST.get('safe'))
        if request.POST.get('role'):
            role = get_object_or_404(Role, name=request.POST.get('role'))
            access_list = SafeAccessControl.objects.filter(safe=safe).filter(object_id=role.id).filter(content_type=ContentType.objects.get_for_model(Role))
        elif request.POST.get('host'):
            host = get_object_or_404(Host, hostname=request.POST.get('host'))
            access_list = SafeAccessControl.objects.filter(safe=safe).filter(object_id=host.id).filter(content_type=ContentType.objects.get_for_model(Host))
        redirect_url = request.POST.get('redirect', reverse('secrets'))
        for control in access_list:
            control.delete()
        messages.add_message(request, messages.SUCCESS, 'removed control(s) from {}'.format(safe.name))
        return redirect(redirect_url)


def create_safe_access(request, *args, **kwargs):
    if request.method == 'POST':
        safe = get_object_or_404(Safe, id=request.POST.get('safe'))
        redirect_url = request.POST.get('redirect', reverse('safe_detail', kwargs={'name': safe.name}))
        if request.POST.get('role'):
            contenttype = ContentType.objects.get_for_model(Role)
            acl_object = get_object_or_404(Role, id=request.POST.get('role'))
        elif request.POST.get('host'):
            contenttype = ContentType.objects.get_for_model(Host)
            acl_object = get_object_or_404(Host, id=request.POST.get('host'))
        try:
            control, created = SafeAccessControl.objects.get_or_create(
                safe=safe, content_type=contenttype, object_id=acl_object.id
            )
            if created:
                message, level = 'added access control', messages.SUCCESS
            else:
                message, level = 'access control already exists', messages.WARNING
            messages.add_message(request, level, message)
        except NameError:
            messages.add_message(request, messages.ERROR, 'host or role was not provided')
        return redirect(redirect_url)