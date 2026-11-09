"""Exports chat messages with their predicted labels to CSV, for reviewing or labelling new training data."""

import csv

from django.core.management.base import BaseCommand

from chat.models import Message


class Command(BaseCommand):
    help = "Export messages and their predicted labels to a CSV file (content,label,score,timestamp)."

    def add_arguments(self, parser):
        parser.add_argument("output", help="Where to write the CSV, e.g. ../ml/data/to_label.csv")
        parser.add_argument("--flagged-only", action="store_true", help="Only messages the classifier flagged.")

    def handle(self, *args, output, flagged_only, **options):
        messages = Message.objects.order_by("timestamp")
        if flagged_only:
            messages = messages.exclude(toxicity_label="non-toxic")
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Same columns as ml/data/train.csv first, so corrected rows can be appended to it.
            writer.writerow(["content", "label", "score", "timestamp"])
            for message in messages.iterator():
                writer.writerow([message.original_content or message.content, message.toxicity_label, message.toxicity_score, message.timestamp.isoformat()])
        self.stdout.write(self.style.SUCCESS(f"Wrote {messages.count()} messages to {output}"))
