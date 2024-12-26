from django.contrib import admin
from .models import Event, Registration_details, Notification, Category, Timeline


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('opportunity_title', 'opportunity_type', 'organization', 'created_by', 'created_at', 'visibility')
    list_filter = ('opportunity_type', 'visibility', 'mode_of_event', 'created_at')

    filter_horizontal = ('categories',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('opportunity_title', 'opportunity_type', 'opportunity_sub_type', 'logo', 'visibility', 'organization', 'mode_of_event')
        }),
        ('Details', {
            'fields': ('website_url', 'festival_name', 'skills_to_be_assessed', 'about_opportunity', 'categories')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at')
        }),
    )


@admin.register(Registration_details)
class RegistrationDetailsAdmin(admin.ModelAdmin):
    list_display = ('event', 'created_by', 'visibility', 'participation_type', 'registration_start', 'registration_end', 'number_of_registration')
    list_filter = ('visibility', 'participation_type', 'registration_start', 'registration_end')
 
    fieldsets = (
        ('Registration Details', {
            'fields': ('event', 'visibility', 'participation_type', 'minimum_members', 'maximum_members', 'registration_start', 'registration_end', 'number_of_registration')
        }),
        ('Users and Clubs', {
            'fields': ('invited_users', 'accepted_users', 'rejected_users', 'invited_club')
        }),
        ('Additional Settings', {
            'fields': ('platform', 'compulsary')
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at', 'status')
    list_filter = ('notification_type', 'is_read', 'created_at', 'updated_at')

    readonly_fields = ('created_at', 'updated_at')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    list_display = ('response', 'event', 'date')
    list_filter = ('date',)

