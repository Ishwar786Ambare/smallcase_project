"""
Management command to update existing support chats with is_ai_only flag.
Run with: python manage.py update_support_chats
"""

from django.core.management.base import BaseCommand
from stocks.models import ChatGroup

class Command(BaseCommand):
    help = 'Updates existing support chats to set is_ai_only flag correctly'

    def handle(self, *args, **options):
        # Get all support chats without the flag set
        support_chats = ChatGroup.objects.filter(
            group_type='support',
            is_ai_only=False  # These were created before the field existed
        )
        
        total = support_chats.count()
        self.stdout.write(f'Found {total} support chats to update')
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No chats to update!'))
            return
        
        # Set all existing support chats to AI-only by default
        # (You can change this logic based on your needs)
        updated = support_chats.update(is_ai_only=True)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated} support chats to is_ai_only=True'
            )
        )
        self.stdout.write('Note: Existing users can still switch to admin support if needed.')
