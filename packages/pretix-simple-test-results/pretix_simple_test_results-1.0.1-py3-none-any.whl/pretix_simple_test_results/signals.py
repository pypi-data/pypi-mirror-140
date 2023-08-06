from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import gettext_noop, ugettext_lazy as _
from i18nfield.rest_framework import I18nField
from i18nfield.strings import LazyI18nString
from pretix.base.settings import settings_hierarkey
from pretix.base.signals import api_event_settings_fields, logentry_display
from pretix.control.signals import nav_event, nav_event_settings
from rest_framework import serializers


@receiver(nav_event_settings, dispatch_uid="simple_test_results_nav")
def navbar_info(sender, request, **kwargs):
    url = resolve(request.path_info)
    if not request.user.has_event_permission(
        request.organizer, request.event, "can_change_event_settings", request=request
    ):
        return []
    return [
        {
            "label": _("Test results"),
            "url": reverse(
                "plugins:pretix_simple_test_results:settings",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.organizer.slug,
                },
            ),
            "active": url.namespace == "plugins:pretix_simple_test_results"
            and url.url_name == "settings",
        },
    ]


@receiver(nav_event, dispatch_uid="simple_test_results_nav")
def navbar_action(sender, request, **kwargs):
    url = resolve(request.path_info)
    if not request.user.has_event_permission(
        request.organizer, request.event, "can_change_orders", request=request
    ):
        return []
    return [
        {
            "label": _("Test results"),
            "url": reverse(
                "plugins:pretix_simple_test_results:index",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.organizer.slug,
                },
            ),
            "icon": "check-square",
            "active": url.namespace == "plugins:pretix_simple_test_results"
            and url.url_name != "settings",
        },
    ]


@receiver(
    signal=api_event_settings_fields,
    dispatch_uid="simple_test_results_api_event_settings_fields",
)
def recv_api_event_settings_fields(sender, **kwargs):
    return {
        "simple_test_results_mail": serializers.BooleanField(required=False),
        "simple_test_results_mail_subject": I18nField(required=False),
        "simple_test_results_mail_body": I18nField(required=False),
        "simple_test_results_sms": serializers.BooleanField(required=False),
        "simple_test_results_sms_text": I18nField(required=False),
    }


@receiver(signal=logentry_display, dispatch_uid="simple_test_results_display")
def badges_logentry_display(sender, logentry, **kwargs):
    if not logentry.action_type.startswith("pretix_simple_test_results."):
        return

    if logentry.action_type == "pretix_simple_test_results.recorded":
        return _("Test result recorded")


settings_hierarkey.add_default("simple_test_results_mail", False, bool)
settings_hierarkey.add_default(
    "simple_test_results_mail_subject",
    LazyI18nString.from_gettext(gettext_noop("Your test result: {result}")),
    LazyI18nString,
)
settings_hierarkey.add_default(
    "simple_test_results_mail_body",
    LazyI18nString.from_gettext(
        gettext_noop(
            "Hello,\n\n"
            "your test result is: {result}.\n\n"
            "Best regards,\n"
            "Your {event} team"
        )
    ),
    LazyI18nString,
)
settings_hierarkey.add_default("simple_test_results_sms", False, bool)
settings_hierarkey.add_default(
    "simple_test_results_sms_text",
    LazyI18nString.from_gettext(gettext_noop("Your test result is: {result}")),
    LazyI18nString,
)
