from django import forms
from .models import CRMConfiguration


class CRMConfigurationForm(forms.ModelForm):
    modules = forms.MultipleChoiceField(choices=CRMConfiguration.MODULES, widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = CRMConfiguration
        fields = ["industry", "modules"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["modules"].initial = self.instance.modules
