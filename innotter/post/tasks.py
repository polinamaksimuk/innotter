import os

from django.core.mail import send_mail
from page.models import Page

from innotter.celery import app


@app.task
def email_for_followers(page_id):
    page = Page.objects.prefetch_related("followers").get(id=page_id)
    users = page.followers.all()
    emails = users.values_list("email", flat=True)
    if emails:
        send_mail(
            subject="hello",
            message=f"Hi! User {page.name} has just been added a new post! Please, check it at Innotter.",
            from_email=os.environ.get("EMAIL_HOST_USER"),
            recipient_list=emails,
        )
