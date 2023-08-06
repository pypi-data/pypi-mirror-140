import logging
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext
from django.views.generic import DetailView, ListView
from pretix.base.email import get_email_context
from pretix.base.i18n import language
from pretix.base.models import Event, OrderPosition, Question, QuestionOption
from pretix.base.services.mail import TolerantDict
from pretix.control import context
from pretix.control.permissions import EventPermissionRequiredMixin
from pretix.control.views.event import EventSettingsFormView, EventSettingsViewMixin

from pretix_simple_test_results.forms import (
    AttendeeFilterForm,
    TestResultsSettingsForm,
    can_use_juvare_api,
)

logger = logging.getLogger(__name__)


class SettingsView(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    form_class = TestResultsSettingsForm
    template_name = "pretix_simple_test_results/settings.html"
    permission = "can_change_event_settings"

    def get_success_url(self) -> str:
        return reverse(
            "plugins:pretix_simple_test_results:settings",
            kwargs={
                "organizer": self.request.event.organizer.slug,
                "event": self.request.event.slug,
            },
        )


class IndexView(EventPermissionRequiredMixin, ListView):
    permission = "can_change_orders"
    template_name = "pretix_simple_test_results/index.html"
    context_object_name = "attendees"
    paginate_by = 100

    def get_queryset(self):
        qs = OrderPosition.objects.select_related("order").filter(
            order__status__in=("n", "p"),
            order__event=self.request.event,
        )

        if self.filter_form.is_valid():
            qs = self.filter_form.filter_qs(qs)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter_form"] = self.filter_form
        return ctx

    @cached_property
    def filter_form(self):
        return AttendeeFilterForm(data=self.request.GET)


class SendView(EventPermissionRequiredMixin, DetailView):
    permission = "can_change_orders"
    template_name = "pretix_simple_test_results/send.html"
    context_object_name = "attendee"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        type_question = self.request.event.questions.get_or_create(
            identifier="test_type",
            defaults={
                "question": gettext("Test type"),
                "type": Question.TYPE_CHOICE,
                "hidden": True,
            },
        )[0]
        ctx['type_options'] = type_question.options.all()
        return ctx

    def get_queryset(self):
        qs = (
            OrderPosition.objects.select_related("order")
            .filter(
                order__status__in=("n", "p"),
                order__event=self.request.event,
            )
            .prefetch_related("answers", "answers__question")
        )
        return qs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        result = request.POST.get("result")

        type_question = self.request.event.questions.get_or_create(
            identifier="test_type",
            defaults={
                "question": gettext("Test type"),
                "type": Question.TYPE_CHOICE,
                "hidden": True,
            },
        )[0]

        try:
            selected_type = type_question.options.get(id=request.POST.get("type"))
        except QuestionOption.DoesNotExist:
            messages.error(request, gettext("Invalid input."))
            return redirect(self.request.get_full_path())

        question = self.request.event.questions.get_or_create(
            identifier="test_result",
            defaults={
                "question": gettext("Test result"),
                "type": Question.TYPE_TEXT,
                "hidden": True,
            },
        )[0]
        question.items.add(self.object.item)
        type_question.items.add(self.object.item)
        self.object.answers.update_or_create(
            question=question,
            defaults={
                "answer": result,
            },
        )
        type_answer = self.object.answers.update_or_create(
            question=question,
            defaults={
                "answer": selected_type.answer,
            },
        )[0]
        type_answer.options.set([selected_type])
        self.object.order.log_action(
            "pretix_simple_test_results.recorded",
            data={"result": result, "type": selected_type.answer,},
            user=self.request.user,
        )

        email_context = get_email_context(
            event=self.request.event, order=self.object.order, position=self.object
        )
        email_context["result"] = result
        email_context["test_type"] = selected_type.answer

        if request.event.settings.simple_test_results_mail:
            with language(self.object.order.locale, self.request.event.settings.region):
                email_template = (
                    self.request.event.settings.simple_test_results_mail_body
                )
                email_subject = str(
                    self.request.event.settings.simple_test_results_mail_subject
                )

                if self.object.attendee_email:
                    self.object.send_mail(
                        email_subject,
                        email_template,
                        email_context,
                        "pretix_simple_test_results.order.position.email.sent",
                    )
                else:
                    self.object.order.send_mail(
                        email_subject,
                        email_template,
                        email_context,
                        "pretix_simple_test_results.order.email.sent",
                    )
        if (
            self.request.event.settings.simple_test_results_sms
            and can_use_juvare_api(self.request.event)
            and self.object.order.phone
        ):
            with language(self.object.order.locale, self.request.event.settings.region):
                from pretix_juvare_notify.tasks import juvare_send_task

                template = self.request.event.settings.simple_test_results_sms_test
                message = str(template).format_map(TolerantDict(email_context))
                juvare_send_task.apply_async(
                    kwargs={
                        "text": message,
                        "to": self.object.order.phone,
                        "event": self.request.event.pk,
                    }
                )

        messages.success(request, gettext("The test result has been sent."))
        if url_has_allowed_host_and_scheme(request.GET.get("backto"), allowed_hosts=[]):
            return redirect(request.GET.get("backto"))
        else:
            return redirect(
                reverse(
                    "plugins:pretix_simple_test_results:index",
                    kwargs={
                        "organizer": self.request.event.organizer.slug,
                        "event": self.request.event.slug,
                    },
                )
            )
