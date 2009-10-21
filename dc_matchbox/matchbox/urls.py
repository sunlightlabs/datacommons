
from django.conf.urls.defaults import patterns

from views import transactions_page, entities_page


urlpatterns = patterns('',
    (r'^transactions', transactions_page),
    (r'^entities', entities_page)
)