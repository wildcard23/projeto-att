from django.contrib import admin

from .models import Task, Location, Frequency, Justification, SuapToken, AuditLog


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "assigned_to", "created_at")
    list_filter = ("status", "assigned_to")
    search_fields = ("title", "description")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude", "radius_meters")
    search_fields = ("name",)


@admin.register(Frequency)
class FrequencyAdmin(admin.ModelAdmin):
    list_display = ("user", "method", "timestamp", "confirmed", "present", "suap_synced")
    list_filter = ("method", "confirmed", "present", "suap_synced")
    search_fields = ("user__username",)


@admin.register(Justification)
class JustificationAdmin(admin.ModelAdmin):
    list_display = ("frequency", "created_at")
    search_fields = ("reason",)


@admin.register(SuapToken)
class SuapTokenAdmin(admin.ModelAdmin):
    list_display = ("access_token", "created_at", "expires_at")
    readonly_fields = ("created_at",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "path", "method", "auth_type", "user", "remote_addr")
    list_filter = ("auth_type", "method")
    search_fields = ("path", "detail", "user__username")
    readonly_fields = ("created_at",)
