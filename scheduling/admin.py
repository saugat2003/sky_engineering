from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q, Count
from datetime import timedelta
from django.utils import timezone

from .models import Meeting, MeetingAttendee


class MeetingAttendeeInline(admin.TabularInline):
    """Inline admin for managing meeting attendees"""
    model = MeetingAttendee
    extra = 1
    fields = ('user', 'rsvp_status', 'added_at')
    readonly_fields = ('added_at',)
    ordering = ('-rsvp_status',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.action(description='Mark selected meetings as completed')
def mark_completed(modeladmin, request, queryset):
    """Bulk action to mark meetings as completed"""
    updated = queryset.update(status='completed')
    modeladmin.message_user(request, f'{updated} meeting(s) marked as completed.')


@admin.action(description='Mark selected meetings as cancelled')
def mark_cancelled(modeladmin, request, queryset):
    """Bulk action to mark meetings as cancelled"""
    updated = queryset.update(status='cancelled')
    modeladmin.message_user(request, f'{updated} meeting(s) cancelled.')


@admin.action(description='Mark selected meetings as scheduled')
def mark_scheduled(modeladmin, request, queryset):
    """Bulk action to mark meetings as scheduled"""
    updated = queryset.update(status='scheduled')
    modeladmin.message_user(request, f'{updated} meeting(s) marked as scheduled.')


class MeetingAdmin(admin.ModelAdmin):
    """Admin interface for Meeting model"""
    
    list_display = (
        'title_display',
        'status_badge',
        'scheduled_date',
        'organiser_display',
        'platform_badge',
        'attendees_count',
        'rsvp_status_summary'
    )
    
    list_filter = (
        'status',
        'platform',
        'recurrence',
        'team',
        ('scheduled_at', admin.DateFieldListFilter),
        'created_at',
    )
    
    search_fields = (
        'title',
        'description',
        'organiser__first_name',
        'organiser__last_name',
        'organiser__email',
        'team__name',
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'attendee_stats',
        'meeting_duration',
        'time_until_meeting',
    )
    
    fieldsets = (
        ('Meeting Details', {
            'fields': ('title', 'description', 'status')
        }),
        ('Schedule', {
            'fields': ('scheduled_at', 'end_time', 'timezone', 'meeting_duration', 'time_until_meeting')
        }),
        ('Platform & Location', {
            'fields': ('platform', 'meeting_link', 'team')
        }),
        ('Organization', {
            'fields': ('organiser', 'recurrence')
        }),
        ('Attendee Statistics', {
            'fields': ('attendee_stats',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = (MeetingAttendeeInline,)
    actions = (mark_completed, mark_cancelled, mark_scheduled)
    
    ordering = ('-scheduled_at',)
    date_hierarchy = 'scheduled_at'
    
    def title_display(self, obj):
        """Display meeting title with link"""
        return format_html(
            '<strong>{}</strong>',
            obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
        )
    title_display.short_description = 'Meeting'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'scheduled': '#17a2b8',  # cyan
            'completed': '#28a745',  # green
            'cancelled': '#dc3545',  # red
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def scheduled_date(self, obj):
        """Display scheduled date and time"""
        return obj.scheduled_at.strftime('%b %d, %Y - %I:%M %p')
    scheduled_date.short_description = 'Scheduled'
    
    def organiser_display(self, obj):
        """Display organiser full name"""
        return obj.organiser.get_full_name() or obj.organiser.username
    organiser_display.short_description = 'Organiser'
    
    def platform_badge(self, obj):
        """Display platform as badge"""
        colors = {
            'zoom': '#2d8cff',
            'teams': '#6264a7',
            'slack': '#e01e5a',
            'google_meet': '#00897b',
            'in_person': '#ff6f00',
            'hybrid': '#7b1fa2',
            'other': '#757575',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.platform, '#757575'),
            obj.get_platform_display()
        )
    platform_badge.short_description = 'Platform'
    
    def attendees_count(self, obj):
        """Display total attendees count"""
        return format_html(
            '<strong style="color: #0066cc;">{}</strong>',
            obj.attendee_count
        )
    attendees_count.short_description = 'Attendees'
    
    def rsvp_status_summary(self, obj):
        """Display RSVP status summary"""
        accepted = obj.accepted_count
        total = obj.attendee_count
        percentage = int((accepted / total * 100) if total > 0 else 0)
        
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">{}/{}</span> ({}%)',
            accepted,
            total,
            percentage
        )
    rsvp_status_summary.short_description = 'RSVPs'
    
    def attendee_stats(self, obj):
        """Display detailed attendee statistics"""
        accepted = obj.attendees.filter(rsvp_status='accepted').count()
        declined = obj.attendees.filter(rsvp_status='declined').count()
        tentative = obj.attendees.filter(rsvp_status='tentative').count()
        pending = obj.attendees.filter(rsvp_status='pending').count()
        
        stats = f"""
        <table style="border-collapse: collapse;">
            <tr style="background-color: #f5f5f5;">
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Status</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Count</strong></td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">✓ Accepted</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #28a745; font-weight: bold;">{accepted}</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 8px; border: 1px solid #ddd;">? Tentative</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #ffc107; font-weight: bold;">{tentative}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">✗ Declined</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #dc3545; font-weight: bold;">{declined}</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td style="padding: 8px; border: 1px solid #ddd;">⊙ Pending</td>
                <td style="padding: 8px; border: 1px solid #ddd; color: #6c757d; font-weight: bold;">{pending}</td>
            </tr>
        </table>
        """
        return format_html(stats)
    attendee_stats.short_description = 'Attendee Statistics'
    
    def meeting_duration(self, obj):
        """Display meeting duration"""
        return f"{obj.duration_minutes} minutes"
    meeting_duration.short_description = 'Duration'
    
    def time_until_meeting(self, obj):
        """Display time until meeting"""
        now = timezone.now()
        diff = obj.scheduled_at - now
        
        if diff.total_seconds() < 0:
            days_ago = abs(diff.days)
            hours_ago = abs(diff.seconds) // 3600
            if days_ago > 0:
                return f"{days_ago} day(s) ago"
            elif hours_ago > 0:
                return f"{hours_ago} hour(s) ago"
            else:
                return "Just now"
        else:
            days_left = diff.days
            hours_left = diff.seconds // 3600
            if days_left > 0:
                return f"In {days_left} day(s)"
            elif hours_left > 0:
                return f"In {hours_left} hour(s)"
            else:
                minutes_left = diff.seconds // 60
                return f"In {minutes_left} minute(s)"
    
    time_until_meeting.short_description = 'Time Status'


class MeetingAttendeeAdmin(admin.ModelAdmin):
    """Admin interface for MeetingAttendee model"""
    
    list_display = (
        'user_name',
        'meeting_title',
        'rsvp_status_display',
        'meeting_date',
        'responded_at'
    )
    
    list_filter = (
        'rsvp_status',
        ('meeting__scheduled_at', admin.DateFieldListFilter),
        'added_at',
    )
    
    search_fields = (
        'user__first_name',
        'user__last_name',
        'user__email',
        'meeting__title',
    )
    
    readonly_fields = ('added_at', 'updated_at')
    
    fieldsets = (
        ('Attendee Information', {
            'fields': ('user', 'meeting')
        }),
        ('RSVP Status', {
            'fields': ('rsvp_status',)
        }),
        ('Timestamps', {
            'fields': ('added_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-meeting__scheduled_at',)
    
    def user_name(self, obj):
        """Display user full name"""
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = 'Attendee'
    
    def meeting_title(self, obj):
        """Display meeting title"""
        return obj.meeting.title[:50]
    meeting_title.short_description = 'Meeting'
    
    def rsvp_status_display(self, obj):
        """Display RSVP status as colored badge"""
        colors = {
            'accepted': '#28a745',  # green
            'declined': '#dc3545',  # red
            'tentative': '#ffc107',  # yellow
            'pending': '#6c757d',   # gray
        }
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.rsvp_status, '#6c757d'),
            'white' if obj.rsvp_status != 'tentative' else 'black',
            obj.get_rsvp_status_display()
        )
    rsvp_status_display.short_description = 'RSVP Status'
    
    def meeting_date(self, obj):
        """Display meeting date"""
        return obj.meeting.scheduled_at.strftime('%b %d, %Y - %I:%M %p')
    meeting_date.short_description = 'Meeting Date'
    
    def responded_at(self, obj):
        """Display response time"""
        if obj.added_at == obj.updated_at:
            return "Not yet responded"
        return obj.updated_at.strftime('%b %d, %Y - %I:%M %p')
    responded_at.short_description = 'Responded'


# Register admin models
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(MeetingAttendee, MeetingAttendeeAdmin)
