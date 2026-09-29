from django import forms
from .models import ToolAccess


class MultiToolAccessForm(forms.ModelForm):
    tools = forms.MultipleChoiceField(
        choices=ToolAccess.TOOLS,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Tools for this user",
    )

    class Meta:
        model = ToolAccess
        fields = ["user", "tools"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["tools"].initial = list(
                ToolAccess.objects.filter(user=self.instance.user).values_list("tool", flat=True)
            )

    def save(self, commit=True):
        selected = self.cleaned_data["tools"]
        user = self.cleaned_data["user"]
        current = self.instance
        current.user = user
        current.tool = selected[0]
        self._selected_tools = selected
        if commit:
            current.save()
            self.save_m2m()
        return current

    def save_m2m(self):
        selected = getattr(self, "_selected_tools", [])
        if not selected:
            return
        user = self.cleaned_data["user"]
        ToolAccess.objects.filter(user=user).exclude(tool__in=selected).delete()
        for tool in selected:
            ToolAccess.objects.get_or_create(user=user, tool=tool)
