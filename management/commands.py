from django.core.management.base import BaseCommand
import schedule
import time


class Command(BaseCommand):
    help = 'Sends notifications every 5 minutes'

    def handle(self, *args, **options):
        # Define the function that sends the notifications
        def send_notifications():
            # Code to send the notifications goes here
            print('Hello')

        # Schedule the function to run every 5 minutes
        schedule.every(5).minutes.do(send_notifications)

        # Run the scheduled tasks in a loop
        while True:
            schedule.run_pending()
            time.sleep(1)
