# Author: 0xsaugat (Saugat Bhattarai)
from django.core.management.base import BaseCommand

from seed import DEFAULT_PASSWORD, seed_database


class Command(BaseCommand):
    help = "Reset and seed the database from the prefilled Team Registry seed data."

    def handle(self, *args, **options):
        # Seed the database and print a summary of the operation.
        summary = seed_database(reset=True, migrate=False)
        self.stdout.write(self.style.SUCCESS("Database reset and seeded from Team Registry.xlsx."))
        for key, value in summary.items():
            self.stdout.write(f"{key}: {value}")
        self.stdout.write(f"Default password for seeded users: {DEFAULT_PASSWORD}")
