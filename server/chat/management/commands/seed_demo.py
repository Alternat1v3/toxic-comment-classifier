"""Creates demo users and a short conversation that goes through the real moderation pipeline."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F

from chat.models import Message
from chat.moderation.pipeline import moderate

User = get_user_model()

USERS = ["ayesha", "bilal", "sara"]

CONVERSATION = [
    ("ayesha", "bilal", "Hey Bilal! Did you finish the database assignment?"),
    ("bilal", "ayesha", "Almost, I'm stuck on the joins part."),
    ("ayesha", "bilal", "Want to go through it together after class?"),
    ("bilal", "ayesha", "Sure. Honestly the lab instructor is a complete idiot."),
    ("ayesha", "bilal", "Haha, careful, the chat flags that kind of thing."),
    ("bilal", "ayesha", "Fine, fine. See you at 5 in the library?"),
    ("ayesha", "bilal", "See you there!"),
    ("sara", "ayesha", "Can you send me the notes from today?"),
]


class Command(BaseCommand):
    help = "Create demo users (ayesha, bilal, sara) and a sample conversation."

    def add_arguments(self, parser):
        parser.add_argument("--password", default="demo-pass-2024", help="Password for the demo users.")
        parser.add_argument(
            "--with-admin",
            action="store_true",
            help="Also create a 'moderator' superuser with the same password, for trying the admin locally. Never use on a real server.",
        )

    @transaction.atomic
    def handle(self, *args, password, with_admin, **options):
        if with_admin and not User.objects.filter(username="moderator").exists():
            User.objects.create_superuser("moderator", "moderator@example.com", password)
            self.stdout.write("Created superuser moderator (admin panel at /admin/)")

        users = {}
        for username in USERS:
            user, created = User.objects.get_or_create(username=username, defaults={"email": f"{username}@example.com"})
            if created:
                user.set_password(password)
                user.save()
            users[username] = user
            self.stdout.write(f"{'Created' if created else 'Found'} user {username}")

        if Message.objects.filter(sender__in=users.values()).exists():
            self.stdout.write("Demo messages already exist; not adding more.")
            return

        for sender, receiver, text in CONVERSATION:
            result = moderate(text)
            prediction = result.prediction
            Message.objects.create(
                sender=users[sender],
                receiver=users[receiver],
                content=result.shown,
                original_content=text,
                toxicity_label=prediction.label,
                toxicity_score=prediction.score,
                classifier=prediction.source,
            )
            if prediction.is_toxic:
                User.objects.filter(pk=users[sender].pk).update(toxic_message_count=F("toxic_message_count") + 1)
            self.stdout.write(f"  {prediction.label:<13} {prediction.score:.2f}  {text}")

        self.stdout.write(self.style.SUCCESS(f"Done. Sign in as any of {', '.join(USERS)} with password '{password}'."))
