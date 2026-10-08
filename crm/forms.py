from django import forms
from .models import Contact, Tag


class ContactForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["tags"].queryset = Tag.objects.filter(owner=user)

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if phone:
            qs = Contact.objects.filter(owner=self._owner, phone=phone)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("A contact with this phone number already exists in your CRM.")
        return phone

    def set_owner(self, owner):
        self._owner = owner

    class Meta:
        model = Contact
        exclude = ["owner"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 4}), "tags": forms.CheckboxSelectMultiple}


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]
