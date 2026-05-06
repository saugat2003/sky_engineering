from django import forms

from .models import Team, TeamEmail


CONTROL_CLASS = (
    'w-full rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm '
    'text-slate-900 shadow-sm transition focus:border-primary focus:outline-none '
    'focus:ring-2 focus:ring-primary/20 dark:border-slate-700 dark:bg-slate-950 '
    'dark:text-slate-100'
)

TEXTAREA_CLASS = (
    'w-full rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm '
    'text-slate-900 shadow-sm transition focus:border-primary focus:outline-none '
    'focus:ring-2 focus:ring-primary/20 dark:border-slate-700 dark:bg-slate-950 '
    'dark:text-slate-100'
)


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            'name',
            'department',
            'team_type',
            'manager',
            'status',
            'mission',
            'description',
            'workstream',
            'development_focus',
            'key_skills',
            'email_address',
            'slack_channel',
            'daily_standup_link',
            'team_wiki_url',
            'jira_project_name',
            'jira_board_link',
            'skills',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': CONTROL_CLASS,
                'placeholder': 'e.g. Playback Reliability',
            }),
            'department': forms.Select(attrs={'class': CONTROL_CLASS}),
            'team_type': forms.Select(attrs={'class': CONTROL_CLASS}),
            'manager': forms.Select(attrs={'class': CONTROL_CLASS}),
            'status': forms.Select(attrs={'class': CONTROL_CLASS}),
            'mission': forms.Textarea(attrs={
                'class': TEXTAREA_CLASS,
                'rows': 4,
                'placeholder': 'What does this team own and why does it exist?',
            }),
            'description': forms.Textarea(attrs={
                'class': TEXTAREA_CLASS,
                'rows': 4,
                'placeholder': 'Optional operating notes, scope, or coverage details.',
            }),
            'workstream': forms.TextInput(attrs={
                'class': CONTROL_CLASS,
                'placeholder': 'e.g. Streaming Experience',
            }),
            'development_focus': forms.Textarea(attrs={
                'class': TEXTAREA_CLASS,
                'rows': 3,
                'placeholder': 'Primary systems, delivery focus, or engineering priorities.',
            }),
            'key_skills': forms.Textarea(attrs={
                'class': TEXTAREA_CLASS,
                'rows': 3,
                'placeholder': 'Comma-separated capabilities or domain strengths.',
            }),
            'email_address': forms.EmailInput(attrs={
                'class': CONTROL_CLASS,
                'placeholder': 'team@example.com',
            }),
            'slack_channel': forms.TextInput(attrs={
                'class': CONTROL_CLASS,
                'placeholder': '#team-channel',
            }),
            'daily_standup_link': forms.URLInput(attrs={
                'class': CONTROL_CLASS,
                'placeholder': 'https://...',
            }),
            'team_wiki_url': forms.URLInput(attrs={
                'class': CONTROL_CLASS,
                'placeholder': 'https://...',
            }),
            'jira_project_name': forms.TextInput(attrs={
                'class': CONTROL_CLASS,
                'placeholder': 'Project key or board name',
            }),
            'jira_board_link': forms.URLInput(attrs={
                'class': CONTROL_CLASS,
                'placeholder': 'https://...',
            }),
            'skills': forms.CheckboxSelectMultiple(attrs={
                'class': 'rounded border-slate-300 text-primary focus:ring-primary',
            }),
        }


class TeamEmailForm(forms.ModelForm):
    class Meta:
        model = TeamEmail
        fields = ['recipient', 'subject', 'message']
        widgets = {
            'recipient': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 dark:border-slate-700 dark:bg-slate-900',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 dark:border-slate-700 dark:bg-slate-900',
                'placeholder': 'Subject',
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 dark:border-slate-700 dark:bg-slate-900',
                'rows': 8,
                'placeholder': 'Write the team message...',
            }),
        }
