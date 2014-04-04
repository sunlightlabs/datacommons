from django.conf.urls.defaults import url, patterns
from piston.resource import Resource
from dcapi.fara.handlers import ContributionFilterHandler, ClientRegistrantFilterHandler, \
    ContactFilterHandler, DisbursementFilterHandler, PaymentFilterHandler
from locksmith.auth.authentication import PistonKeyAuthentication

ad = { 'authentication': PistonKeyAuthentication() }
contribution_filter_handler = Resource(ContributionFilterHandler, **ad)
client_registrant_filter_handler = Resource(ClientRegistrantFilterHandler, **ad)
contact_filter_handler = Resource(ContactFilterHandler, **ad)
disbursement_filter_handler = Resource(DisbursementFilterHandler, **ad)
payment_filter_handler = Resource(PaymentFilterHandler, **ad)

urlpatterns = patterns('',
    url(r'^/contribution.(?P<emitter_format>csv|json|xls)$', contribution_filter_handler, name='api_fara_contribution_filter'),
    url(r'^/client_registrant.(?P<emitter_format>csv|json|xls)$', client_registrant_filter_handler, name='api_fara_client_filter'),
    url(r'^/contact.(?P<emitter_format>csv|json|xls)$', contact_filter_handler, name='api_fara_contact_filter'),
    url(r'^/disbursement.(?P<emitter_format>csv|json|xls)$', disbursement_filter_handler, name='api_fara_disbursement_filter'),
    url(r'^/payment.(?P<emitter_format>csv|json|xls)$', payment_filter_handler, name='api_fara_payment_filter')
)
