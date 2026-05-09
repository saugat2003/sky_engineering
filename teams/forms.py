# Authorship: Teams module authored by 0xsaugat.
from django import forms

from .models import Skill, Team, TeamDependency, TeamEmail


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
        # Core fields exposed in the team create/update flow.
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
        # Apply consistent form styling to the team email fields.
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


class TeamDependencyForm(forms.ModelForm):
    class Meta:
        model = TeamDependency
        fields = ['to_team', 'dependency_type', 'description']
        # Provide concise placeholders to guide dependency entry.
        widgets = {
            'to_team': forms.Select(attrs={'class': CONTROL_CLASS}),
            'dependency_type': forms.TextInput(attrs={
                'class': CONTROL_CLASS,
                'placeholder': 'e.g. API, data feed, deployment dependency',
            }),
            'description': forms.Textarea(attrs={
                'class': TEXTAREA_CLASS,
                'rows': 3,
                'placeholder': 'Short note explaining the dependency.',
            }),
        }

    def __init__(self, *args, source_team=None, **kwargs):
        # Filter the dependency picker to avoid self-references.
        super().__init__(*args, **kwargs)
        self.source_team = source_team
        queryset = Team.objects.all()
        if source_team:
            queryset = queryset.exclude(pk=source_team.pk)
        self.fields['to_team'].queryset = queryset.order_by('name')

    def clean_to_team(self):
        # Enforce unique, non-self dependencies at the form layer.
        to_team = self.cleaned_data['to_team']
        if self.source_team and to_team.pk == self.source_team.pk:
            raise forms.ValidationError('A team cannot depend on itself.')
        if self.source_team and TeamDependency.objects.filter(from_team=self.source_team, to_team=to_team).exists():
            raise forms.ValidationError('This dependency already exists.')
        return to_team


class TeamSkillForm(forms.Form):
    skill = forms.ModelChoiceField(
        queryset=Skill.objects.none(),
        widget=forms.Select(attrs={'class': CONTROL_CLASS}),
        label='Skill',
    )

    def __init__(self, *args, team=None, **kwargs):
        # Limit selectable skills to those not already assigned.
        super().__init__(*args, **kwargs)
        queryset = Skill.objects.order_by('name')
        if team:
            queryset = queryset.exclude(pk__in=team.skills.values_list('pk', flat=True))
        self.fields['skill'].queryset = queryset
