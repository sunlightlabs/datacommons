from django import forms
from dcentity.models import entityref_cache

class AssociationForm(forms.Form):
    
    transactions = forms.CharField(widget=forms.Textarea())
    
    def __init__(self, model, entity_id, *args, **kwargs):

        super(AssociationForm, self).__init__(*args, **kwargs)
        
        choices = [(f, f) for f in entityref_cache[model]]
        self.fields['column'] = forms.ChoiceField(
                                    required=True,
                                    label='Associate records to',
                                    choices=choices)
        
        self.fields['entity_id'] = forms.CharField(
                                    initial=entity_id,
                                    widget=forms.HiddenInput())
        
        self.fields['action'] = forms.ChoiceField(
                                    required=True,
                                    label='These transactions should be',
                                    choices=(
                                        ('add','related to entity'),
                                        ('remove','removed from entity'),
                                    ))