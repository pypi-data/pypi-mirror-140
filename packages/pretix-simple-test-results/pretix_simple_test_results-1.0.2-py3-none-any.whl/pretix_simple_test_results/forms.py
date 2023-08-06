from django import forms
from django.conf import settings
from django.db.models import Exists, Max, OuterRef, Q, Subquery
from django.db.models.functions import Upper
from django.utils.translation import gettext_lazy as _
from i18nfield.forms import I18nFormField, I18nTextarea, I18nTextInput
from pretix.base.email import get_available_placeholders
from pretix.base.forms import PlaceholderValidator, SettingsForm
from pretix.base.models import Checkin, QuestionAnswer
from pretix.control.forms.filter import FilterForm


def can_use_juvare_api(event):
    try:
        import pretix_juvare_notify  # noqa
    except ImportError:
        return settings.DEBUG
    # Is the plugin active
    if "pretix_juvare_notify" not in event.plugins:
        return False
    # Is the plugin configured
    if not event.settings.juvare_client_secret:
        return False
    return True


class TestResultsSettingsForm(SettingsForm):
    simple_test_results_mail = forms.BooleanField(
        label=_("Send test result via email"),
        required=False,
    )
    simple_test_results_mail_subject = I18nFormField(
        label=_("Email Subject"),
        required=True,
        widget=I18nTextInput,
    )
    simple_test_results_mail_body = I18nFormField(
        label=_("Email Body"),
        required=True,
        widget=I18nTextarea,
    )
    simple_test_results_sms = forms.BooleanField(
        label=_("Send test result via SMS"),
        help_text=_("Uses the Juvare Notify API"),
        required=False,
    )
    simple_test_results_sms_text = I18nFormField(
        label=_("SMS Body"),
        required=True,
        widget=I18nTextarea,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = kwargs.pop("obj")

        self._set_field_placeholders(
            "simple_test_results_mail_subject",
            ["event", "order", "position"],
            ["{result}", "{test_type}"],
        )
        self._set_field_placeholders(
            "simple_test_results_mail_body",
            ["event", "order", "position"],
            ["{result}", "{test_type}"],
        )
        self._set_field_placeholders(
            "simple_test_results_sms_text", ["event", "order", "position"], ["{result}", "{test_type}"]
        )
        if not can_use_juvare_api(self.event):
            self.fields.pop("simple_test_results_sms")
            self.fields.pop("simple_test_results_sms_text")

    def _set_field_placeholders(self, fn, base_parameters, extras=[]):
        phs = extras + [
            "{%s}" % p
            for p in sorted(
                get_available_placeholders(self.event, base_parameters).keys()
            )
        ]
        ht = _("Available placeholders: {list}").format(list=", ".join(phs))
        if self.fields[fn].help_text:
            self.fields[fn].help_text += " " + str(ht)
        else:
            self.fields[fn].help_text = ht
        self.fields[fn].validators.append(PlaceholderValidator(phs))


class AttendeeFilterForm(FilterForm):
    orders = {
        "attendee_name": "attendee_name_cached",
        "-attendee_name": "-attendee_name_cached",
        "last_checkin": "last_checkin",
        "-last_checkin": "-last_checkin",
    }
    query = forms.CharField(
        label=_("Search query"),
        widget=forms.TextInput(
            attrs={"placeholder": _("Search query"), "autofocus": "autofocus"}
        ),
        required=False,
    )
    state = forms.ChoiceField(
        label=_("Status"),
        choices=[
            ("", _("Checked in and no result")),
            ("nores", _("No result")),
        ],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def filter_qs(self, qs):
        fdata = self.cleaned_data

        if fdata.get("query"):
            query = fdata.get("query")
            qs = qs.filter(
                Q(secret__icontains=query)
                | Q(attendee_name_cached__icontains=query)
                | Q(order__email__icontains=query)
                | Q(attendee__email__icontains=query)
                | Q(order__phone__icontains=query)
            )

        has_res = Exists(
            QuestionAnswer.objects.filter(
                orderposition=OuterRef("pk"), question__identifier="test_result"
            )
        )
        cqs = (
            Checkin.objects.filter(
                position_id=OuterRef("pk"),
            )
            .order_by()
            .values("position_id")
            .annotate(m=Max("datetime"))
            .values("m")
        )
        qs = qs.annotate(last_checkin=Subquery(cqs))
        if fdata.get("state") == "nores":
            qs = qs.exclude(has_res)
        else:
            qs = qs.exclude(has_res).filter(last_checkin__isnull=False)

        if fdata.get("ordering"):
            qs = qs.order_by(self.get_order_by())
        else:
            qs = qs.order_by("last_checkin")

        return qs
