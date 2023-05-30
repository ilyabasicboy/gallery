from django.urls import path
from .views import FilesView, UploadFileView, SlotView, XmppAuthView, TokensView,\
    QuotaView, AccountListView, AccountView, XmppCodeView, AvatarView, StatsView, OpenGraphView


urlpatterns = [
    path('files/', FilesView.as_view({'get': 'list', 'delete': 'delete'}), name='files'),
    path('files/upload/', UploadFileView.as_view(), name='files_upload'),
    path('files/slot/', SlotView.as_view(), name='slot'),
    path(r'files/stats/', StatsView.as_view(), name='stats'),
    path('avatar/', AvatarView.as_view({'get': 'list', 'delete': 'delete'}), name='avatar'),
    path('avatar/upload/', UploadFileView.as_view(), {'is_avatar': True}, name='avatar_upload'),
    path('account/xmpp_code_request/', XmppCodeView.as_view(), name='xmpp_code_request'),
    path('account/xmpp_auth/', XmppAuthView.as_view(), name='xmpp_auth'),
    path('account/tokens/', TokensView.as_view({'get': 'list', 'delete': 'delete'}), name='tokens'),
    path('account/quota/', QuotaView.as_view(), name='quota'),
    path('account/', AccountView.as_view({'delete': 'delete'}), name='account'),
    path('account/list/', AccountListView.as_view(), name='account_list'),
    path(r'opengraph/', OpenGraphView.as_view(), name='opengraph'),
]
