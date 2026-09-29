from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import ToolAccess
from .forms import MultiToolAccessForm


class ToolAccessInline(admin.TabularInline):
    model = ToolAccess
    extra = 1
    max_num = 4


class UserAdmin(BaseUserAdmin):
    inlines = [ToolAccessInline]


@admin.register(ToolAccess)
class ToolAccessAdmin(admin.ModelAdmin):
    form = MultiToolAccessForm
    list_display = ("user", "tool", "granted_at")
    list_filter = ("tool",)
    search_fields = ("user__username", "user__email")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
