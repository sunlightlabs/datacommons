from django.conf.urls.defaults import url, patterns
from piston.resource import Resource
from dcapi.reconcile.handlers import EntityReconciliationHandler

entityreconciliation_handler = Resource(EntityReconciliationHandler)

urlpatterns = patterns('',
        url(r'^reconcile/?$', entityreconciliation_handler, {'emitter_format':'json', 'name': 'api_entity_reconciler'}),
)
