from django.test import SimpleTestCase
from django.urls import reverse, resolve
from gallery_new.api.views import FilesView, UploadFileView, SlotView, StatsView, AvatarView, XmppCodeView,\
    XmppAuthView, TokensView, QuotaView, AccountView, AccountListView, OpenGraphView


class TestUrls(SimpleTestCase):

    def test_files_url(self):
        url = reverse('files')
        self.assertEquals(resolve(url).func.cls, FilesView)

    def test_files_upload_url(self):
        url = reverse('files_upload')
        self.assertEquals(resolve(url).func.cls, UploadFileView)

    def test_slot_url(self):
        url = reverse('slot')
        self.assertEquals(resolve(url).func.cls, SlotView)

    def test_stats_url(self):
        url = reverse('stats')
        self.assertEquals(resolve(url).func.cls, StatsView)

    def test_avatar_url(self):
        url = reverse('avatar')
        self.assertEquals(resolve(url).func.cls, AvatarView)

    def test_avatar_upload_url(self):
        url = reverse('avatar_upload')
        self.assertEquals(resolve(url).func.cls, UploadFileView)

    def test_xmpp_code_request_url(self):
        url = reverse('xmpp_code_request')
        self.assertEquals(resolve(url).func.cls, XmppCodeView)

    def test_xmpp_auth_url(self):
        url = reverse('xmpp_auth')
        self.assertEquals(resolve(url).func.cls, XmppAuthView)

    def test_tokens_url(self):
        url = reverse('tokens')
        self.assertEquals(resolve(url).func.cls, TokensView)

    def test_quota_url(self):
        url = reverse('quota')
        self.assertEquals(resolve(url).func.cls, QuotaView)

    def test_account_url(self):
        url = reverse('account')
        self.assertEquals(resolve(url).func.cls, AccountView)

    def test_account_list_url(self):
        url = reverse('account_list')
        self.assertEquals(resolve(url).func.cls, AccountListView)

    def test_opengraph_url(self):
        url = reverse('opengraph')
        self.assertEquals(resolve(url).func.cls, OpenGraphView)