from django.conf.urls import url

from .views import IndexView, SendView, SettingsView

urlpatterns = [
    url(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/settings/simple_test_results/$",
        SettingsView.as_view(),
        name="settings",
    ),
    url(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/simple_test_results/$",
        IndexView.as_view(),
        name="index",
    ),
    url(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/simple_test_results/(?P<pk>[^/]+)/send/$",
        SendView.as_view(),
        name="send",
    ),
]
