from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import View

from nautobot.dcim.models import RearPort, Cable, CablePath, Device
from nautobot.core.views.generic import (
    BulkDeleteView, BulkImportView, GetReturnURLMixin, ObjectEditView,
    ObjectListView
)

import time

from . import filters, forms, tables
from .models import CableTemplate, MeasurementLog


class ReconnectView(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = 'dcim.add_cable'
    template_name = 'nautobot_cable_utils/cable_connect.html'

    def dispatch(self, request, *args, pk=None, **kwargs):
        self.obj = Cable.objects.get(pk=pk)

        idx = (self.obj.termination_a_type.model, self.obj.termination_b_type.model)
        idx_sorted = tuple(sorted(idx))
        if idx != idx_sorted:
            termination_a = self.obj.termination_a
            self.obj.termination_a = self.obj.termination_b
            self.obj.termination_b = termination_a

        self.form_class = {
            ('circuittermination', 'circuittermination'): forms.ConnectCircuitTerminationForm,
            ('circuittermination', 'rearport'): forms.ConnectCircuitTerminationToRearPortForm,
            ('consoleport', 'consoleserverport'): forms.ConnectConsolePortToConsoleServerPortForm,
            ('consoleport', 'frontport'): forms.ConnectConsolePortToFrontPortForm,
            ('consoleport', 'rearport'): forms.ConnectConsolePortToRearPortForm,
            ('consoleserverport', 'frontport'): forms.ConnectConsoleServerPortToFrontPortForm,
            ('consoleserverport', 'rearport'): forms.ConnectConsoleServerPortToRearPortForm,
            ('powerfeed', 'powerport'): forms.ConnectPowerfeedToPowerPortForm,
            ('poweroutlet', 'powerport'): forms.ConnectPowerOutletToPowerPortForm,
            ('circuittermination', 'interface'): forms.ConnectCircuitTerminationToInterfaceForm,
            ('frontport', 'interface'): forms.ConnectFrontPortToInterfaceForm,
            ('interface', 'rearport'): forms.ConnectInterfaceToRearPortForm,
            ('interface', 'interface'): forms.ConnectInterfaceForm,
            ('frontport', 'frontport'): forms.ConnectFrontPortForm,
            ('frontport', 'rearport'): forms.ConnectFrontPortToRearPortForm,
            ('circuittermination', 'frontport'): forms.ConnectCircuitTerminationToFrontPortForm,
            ('rearport', 'rearport'): forms.ConnectRearPortForm,
        }[idx_sorted]

        return super().dispatch(request, *args, **kwargs)

    def prefill_form(self, initial_data, termination):
        o = getattr(self.obj, termination)
        if o and hasattr(o, 'device'):
            device = o.device
            initial_data['{}_device'.format(termination)] = device
            if device.site:
                initial_data['{}_site'.format(termination)] = device.site
            if device.rack:
                initial_data['{}_rack'.format(termination)] = device.rack

    def get(self, request, *args, **kwargs):
        # Parse initial data manually to avoid setting field values as lists
        initial_data = {k: request.GET[k] for k in request.GET}

        self.prefill_form(initial_data, 'termination_a')
        self.prefill_form(initial_data, 'termination_b')

        form = self.form_class(instance=self.obj, initial=initial_data)

        return render(request, self.template_name, {
            'obj': self.obj,
            'obj_type': Cable._meta.verbose_name,
            'form': form,
            'return_url': self.get_return_url(request, self.obj),
        })

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                if hasattr(self.obj.termination_a, '_path') and self.obj.termination_a._path_id:
                    self.obj.termination_a._path = None
            except CablePath.DoesNotExist:
                pass
            try:
                if hasattr(self.obj.termination_b, '_path') and self.obj.termination_b._path_id:
                    self.obj.termination_b._path = None
            except CablePath.DoesNotExist:
                pass
            self.obj.delete()
            self.obj.pk = None
            self.obj._state.adding = True

            self.obj.termination_a.cable = None
            self.obj.termination_b.cable = None

            form = self.form_class(request.POST, request.FILES, instance=self.obj)
            if form.is_valid():
                obj = form.save()

                redirect_url = self.get_return_url(request, obj)
                return redirect(redirect_url)

            return render(request, self.template_name, {
                'obj': self.obj,
                'obj_type': Cable._meta.verbose_name,
                'form': form,
                'return_url': self.get_return_url(request, self.obj),
            })


class CommissionView(PermissionRequiredMixin, GetReturnURLMixin, View):
    permission_required = 'dcim.edit_cable'
    template_name = 'nautobot_cable_utils/commission_cable.html'

    def get(self, request, pk=None):
        cable = get_object_or_404(Cable, pk=pk)
        form = forms.CommissionForm(initial={'cable': cable})

        return render(request, self.template_name, {
            'form': form,
            'cable': cable,
        })

    def post(self, request, pk=None):
        cable = get_object_or_404(Cable, pk=pk)
        form = forms.CommissionForm(request.POST, initial={'cable': cable})

        if form.is_valid():
            form.save()

            return redirect(self.get_return_url(request, cable))

        return render(request, self.template_name, {
            'form': form,
            'cable': cable,
        })


class CableTemplateListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_cable_template'
    queryset = CableTemplate.objects.all()
    filterset = filters.CableTemplateFilterSet
    filterset_form = forms.CableTemplateFilterForm
    table = tables.CableTemplateTable
    action_buttons = tuple()
    template_name = 'nautobot_cable_utils/cable_template_list.html'


class CableTemplateCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_cable_template'
    queryset = CableTemplate.objects.all()
    model_form = forms.CableTemplateForm
    default_return_url = 'plugins:nautobot_cable_utils:cabletemplate_list'


class CableTemplateEditView(CableTemplateCreateView):
    permission_required = 'dcim.edit_cable_template'


class CableTemplateBulkImportView(BulkImportView):
    queryset = CableTemplate.objects.all()
    model_form = forms.CableTemplateCSVForm
    table = tables.CableTemplateTable


class CableTemplateBulkDeleteView(BulkDeleteView):
    queryset = CableTemplate.objects.all()
    filterset = filters.CableTemplateFilterSet
    table = tables.CableTemplateTable


class MeasurementLogListView(PermissionRequiredMixin, ObjectListView):
    permission_required = 'dcim.view_measurement_log'
    queryset = MeasurementLog.objects.all()
    table = tables.MeasurementLogTable
    action_buttons = tuple()
    template_name = 'nautobot_cable_utils/measurement_log_list.html'


class MeasurementLogCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.add_measurement_log'
    queryset = MeasurementLog.objects.all()
    model_form = forms.MeasurementLogForm
    default_return_url = 'plugins:nautobot_cable_utils:measurement_log_list'


class MeasurementLogEditView(CableTemplateCreateView):
    permission_required = 'dcim.edit_measurement_log'


class MeasurementLogBulkDeleteView(BulkDeleteView):
    queryset = MeasurementLog.objects.all()
    table = tables.MeasurementLogTable
