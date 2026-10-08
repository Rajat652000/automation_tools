from django import forms
from .models import Segment


class SegmentForm(forms.ModelForm):
    field = forms.ChoiceField(choices=[("city", "City"), ("status", "Status"), ("category", "Category"), ("source", "Source")])
    operator = forms.ChoiceField(choices=[("equals", "Equals"), ("contains", "Contains")])
    value = forms.CharField(max_length=150)

    class Meta:
        model = Segment
        fields = ["name", "description"]
