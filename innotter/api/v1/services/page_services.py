from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from page.models import Page
from person.models import User
from rest_framework.response import Response


class PageServices:
    @classmethod
    def add_user_to_followers(cls, page: Page, user_id: int) -> None:
        user = get_object_or_404(User, pk=user_id)
        if user in page.follow_requests.all():
            page.follow_requests.remove(user.pk)
            page.followers.add(user.pk)

    @classmethod
    def add_all_users_to_followers(cls, page: Page) -> None:
        for user in page.follow_requests.all():
            cls.add_user_to_followers(page, user.pk)

    @classmethod
    def remove_user_from_requests(cls, page: Page, user_id: int) -> None:
        user = get_object_or_404(User, pk=user_id)
        if user in page.follow_requests.all():
            page.follow_requests.remove(user.pk)

    @classmethod
    def remove_all_users_from_requests(cls, page: Page) -> None:
        for user in page.follow_requests.all():
            cls.remove_user_from_requests(page, user.pk)

    @classmethod
    def is_user_in_page_followers(cls, user, page: Page):
        return page.followers.filter(id=user.pk).exists()

    @classmethod
    def is_user_in_page_follow_requests(cls, user, page):
        return page.follow_requests.filter(id=user.pk).exists()

    @classmethod
    def add_user_to_page_follow_requests(cls, user, page):
        page.follow_requests.add(user)

    @classmethod
    def add_user_to_page_followers(cls, user, page):
        page.followers.add(user)

    @classmethod
    def remove_user_from_followers(cls, page: Page, user) -> None:
        page.followers.remove(user)

    @classmethod
    def add_follow_requests_to_request_data(cls, request_data, follow_requests):
        follow_requests = list(follow_requests.values_list("pk", flat=True))
        request_data.update({"follow_requests": follow_requests})
        return request_data

    @classmethod
    def is_page_unblocked(cls, unblock_date):
        return timezone.now() >= unblock_date

    @classmethod
    def get_page_followers(cls, page_pk: int) -> Page:
        return get_object_or_404(Page, pk=page_pk).followers.all().order_by("id")

    @classmethod
    def get_page_follow_requests(cls, page_pk: int) -> Response:
        return get_object_or_404(Page, pk=page_pk).follow_requests.all().order_by("id")

    @classmethod
    def get_blocked_pages(cls) -> QuerySet[Page, ...]:
        return Page.objects.filter(is_blocked=True).order_by("id")

    @classmethod
    def get_unblocked_pages(cls, is_owner_page: bool, owner=None) -> QuerySet[Page, ...]:
        pages = Page.objects.filter(
            Q(is_blocked=False),
            Q(unblock_date__isnull=True) | Q(unblock_date__lt=timezone.now()),
        ).order_by("id")
        if is_owner_page:
            pages = pages.filter(owner=owner)
        return pages
