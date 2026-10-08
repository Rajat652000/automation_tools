from .models import CRMConfiguration


def crm_config(request):
    if not request.user.is_authenticated:
        return {"crm_configuration": None}
    return {"crm_configuration": CRMConfiguration.objects.filter(owner=request.user).first()}
