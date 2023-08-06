from nautobot.dcim.choices import CableStatusChoices
from nautobot.extras.plugins import PluginTemplateExtension

from .models import MeasurementLog


class DeviceBulkConnect(PluginTemplateExtension):
    model = 'dcim.cable'

    def buttons(self):
        cable = self.context['object']
        log = None
        maybe_log = MeasurementLog.objects.filter(cable=cable)
        if maybe_log.exists():
            log = maybe_log.first().link
        return self.render('nautobot_cable_utils/inc/buttons.html', {
            'cable': cable,
            'cable_planned': cable.status.slug == CableStatusChoices.STATUS_PLANNED,
            'log': log,
        })


template_extensions = [DeviceBulkConnect]
