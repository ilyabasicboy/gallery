from django.urls import path
from .views import FilesView, UploadFileView, SlotView, XmppAuthView, TokensView,\
    QuotaView, AccountListView, AccountView, XmppCodeView, AvatarView, StatsView, OpenGraphView


urlpatterns = [
    path('files/', FilesView.as_view({'get': 'list', 'delete': 'delete'})),
    path('files/upload/', UploadFileView.as_view()),
    path('files/slot/', SlotView.as_view()),
    path(r'files/stats/', StatsView.as_view()),
    path('avatar/', AvatarView.as_view({'get': 'list', 'delete': 'delete'})),
    path('avatar/upload/', UploadFileView.as_view(), {'is_avatar': True}, name='avatar_upload'),
    path('account/xmpp_code_request/', XmppCodeView.as_view()),
    path('account/xmpp_auth/', XmppAuthView.as_view(), name='xmpp_auth'),
    path('account/tokens/', TokensView.as_view({'get': 'list', 'delete': 'delete'})),
    path('account/quota/', QuotaView.as_view()),
    path('account/', AccountView.as_view({'delete': 'delete'})),
    path('account/list/', AccountListView.as_view()),
    path(r'opengraph/', OpenGraphView.as_view()),
]
