from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured

class Command(BaseCommand):

    help = "list fields on a model"
    args = "<app_label> <model_label>"

    requires_model_validation = False
    
    def handle(self, app_label, model_label=None, *args, **options):
        
        from django.db.models import get_app, get_model, get_models
        
        try:
            
            app = get_app(app_label)
            
            if model_label:
                models = (get_model(app_label, model_label),)
            else:
                models = get_models(app)
            
            model_fields = { }

            for model in models:
                model_fields[model._meta.object_name] = [field.name for field in model._meta.fields]
            
            print repr(model_fields)
            
        except ImproperlyConfigured, ic:
            print "*** %s" % ic.message
