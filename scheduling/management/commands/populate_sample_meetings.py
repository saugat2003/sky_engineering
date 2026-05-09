"""Populate sample meeting data for development.
Author: Bijay Bikram Dahal
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from teams.models import Team
from scheduling.models import Meeting, MeetingAttendee


class Command(BaseCommand):
    help = 'Populate database with sample meetings for testing and demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=30,
            help='Number of sample meetings to create (default: 30)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing meetings before creating new ones'
        )

    def handle(self, *args, **options):
        if options['clear']:
            Meeting.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared all existing meetings'))

        count = options['count']
        users = list(User.objects.filter(is_active=True))
        teams = list(Team.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR('No active users found. Please create users first.'))
            return

        meeting_titles = [
            'Team Standup',
            'Project Review',
            'Client Demo',
            'Budget Planning',
            'Sprint Planning',
            'Code Review Session',
            'Design Sync',
            'Marketing Strategy',
            'Performance Analysis',
            'Infrastructure Planning',
            'Database Optimization',
            'User Research Findings',
            'Quarterly Business Review',
            'Product Roadmap Discussion',
            'Security Audit Review',
            'Customer Feedback Session',
            'Team Building Activity',
            'Training Workshop',
            'Mentoring Session',
            'Architecture Review',
            'UI/UX Presentation',
            'Release Planning',
            'Retrospective Meeting',
            'Stakeholder Update',
            'Technical Deep Dive',
        ]

        meeting_descriptions = [
            'Discuss progress on current sprint and blockers',
            'Review project metrics and deliverables',
            'Demonstrate new features to client',
            'Plan budget allocation for next quarter',
            'Plan and estimate work for upcoming sprint',
            'Review code changes and architecture',
            'Align on design system and components',
            'Discuss marketing campaigns and initiatives',
            'Analyze performance metrics and optimization opportunities',
            'Plan infrastructure upgrades and scaling',
            'Optimize database queries and indexes',
            'Share insights from user research',
            'Review quarterly goals and achievements',
            'Discuss product priorities and timeline',
            'Review security policies and compliance',
            'Gather and discuss customer feedback',
            'Team bonding and social activities',
            'Technical skills training and development',
            'One-on-one mentoring and guidance',
            'Review system architecture and design patterns',
            'Present new UI/UX improvements',
            'Coordinate release schedule and milestones',
            'Reflect on sprint and discuss improvements',
            'Update stakeholders on progress',
            'Deep dive into technical topic',
        ]

        platforms = ['zoom', 'teams', 'slack', 'google_meet', 'in_person', 'hybrid', 'other']
        statuses = ['scheduled', 'completed', 'cancelled']
        recurrences = ['none', 'daily', 'weekly', 'biweekly', 'monthly']

        created_count = 0
        now = timezone.now()

        for i in range(count):
            # Random date within next 90 days, with some in past for "completed"
            days_offset = random.randint(-14, 90)
            meeting_date = now + timedelta(days=days_offset)
            
            # Random time between 9 AM and 5 PM
            meeting_date = meeting_date.replace(
                hour=random.randint(9, 16),
                minute=random.choice([0, 15, 30, 45]),
                second=0,
                microsecond=0
            )

            # Duration between 30 and 120 minutes
            duration = random.randint(3, 12) * 10

            # Status based on date
            if days_offset < -1:
                status = random.choice(['completed', 'cancelled'])
            else:
                status = 'scheduled'

            organizer = random.choice(users)
            team = random.choice(teams) if teams and random.random() > 0.3 else None

            meeting = Meeting.objects.create(
                title=random.choice(meeting_titles),
                description=random.choice(meeting_descriptions),
                scheduled_at=meeting_date,
                duration_minutes=duration,
                platform=random.choice(platforms),
                meeting_link='https://zoom.us/j/' + str(random.randint(1000000000, 9999999999)) if random.random() > 0.3 else None,
                organiser=organizer,
                team=team,
                status=status,
                timezone='UTC',
                recurrence=random.choice(recurrences),
            )

            # Add 2-8 attendees
            num_attendees = random.randint(2, 8)
            available_attendees = [u for u in users if u != organizer]
            
            if available_attendees:
                attendees = random.sample(
                    available_attendees,
                    min(num_attendees, len(available_attendees))
                )

                for attendee in attendees:
                    # Past meetings: more completed statuses; future meetings: more pending
                    if days_offset < -1:
                        rsvp_status = random.choices(
                            ['accepted', 'declined', 'tentative', 'pending'],
                            weights=[40, 20, 15, 25]
                        )[0]
                    else:
                        rsvp_status = random.choices(
                            ['accepted', 'declined', 'tentative', 'pending'],
                            weights=[35, 10, 15, 40]
                        )[0]

                    MeetingAttendee.objects.create(
                        meeting=meeting,
                        user=attendee,
                        rsvp_status=rsvp_status
                    )

            created_count += 1

            if created_count % 10 == 0:
                self.stdout.write(
                    self.style.WARNING(f'Created {created_count}/{count} meetings...')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample meetings!')
        )
        self.stdout.write(
            self.style.SUCCESS('Run "python manage.py runserver" to see the calendar')
        )
