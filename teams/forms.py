from django import forms

from .models import TeamEmail


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
