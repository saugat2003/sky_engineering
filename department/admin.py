"""Admin registrations for the department app.
Author: Rupesh Dahal
"""

from django.contrib import admin

from department.models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
	list_display = ("name", "head", "is_active", "created_at", "updated_at")
	search_fields = ("name", "description", "specialisation", "head__username")
	list_filter = ("is_active", "created_at")
	ordering = ("name",)
	autocomplete_fields = ("head",)
	list_select_related = ("head",)
	readonly_fields = ("created_at", "updated_at")
	fieldsets = (
		(None, {"fields": ("name", "description", "specialisation")}),
		("Leadership", {"fields": ("head",)}),
		("Status", {"fields": ("is_active",)}),
		("Timestamps", {"fields": ("created_at", "updated_at")}),
	)