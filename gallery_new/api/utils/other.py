from django.conf import settings
from gallery_new.api.models import EntityFile
import xmpp


def is_blacklisted_or_not_whitelisted(device: str, username: str) -> bool:

    """ Check username in black and white list"""

    try:
        black_list = settings.BLACK_LIST
    except AttributeError:
        black_list = []
    try:
        white_list = settings.WHITE_LIST
    except AttributeError:
        white_list = []
    result = False
    if black_list:
        result = device in black_list or username in black_list
    if white_list:
        result = device not in white_list or username not in white_list
    return result


def send_code(
        sjid: str, password: str,
        code: str, srecipient: str,
        stanza_id: str,
        stanza_type: str, url: str) -> bool:

    """ Send verification code """

    # try, except for using threading
    try:
        jid = xmpp.protocol.JID(sjid)
        recipient = xmpp.protocol.JID(srecipient)
        cl = xmpp.Client(jid.getDomain(), debug=[])
        con = cl.connect()
        if not con:
            print('Error connecting to the XMPP server')
            return False
        auth = cl.auth(jid.getNode(), password, resource=jid.getResource())
        if not auth:
            print('Authentication error on XMPP server')
            return False
        if stanza_type == 'message':
            packet = xmpp.protocol.Message(recipient, 'Verification code is {}'.format(code),
                                           'chat', payload=[xmpp.protocol.Node('urn:xmpp:hints no-store')])
            if recipient.getResource():
                packet.addChild(name='private', namespace='urn:xmpp:carbons:2')
                packet.addChild(name='no-copy', namespace='urn:xmpp:hints')
        else:
            packet = xmpp.protocol.Iq(typ='get', to=recipient)

        packet.addChild(name='confirm', attrs={'id': code, 'url': url},
                        namespace='http://jabber.org/protocol/http-auth')
        packet.setAttr('id', stanza_id)
        cl.send(packet)
        cl.disconnect()
    except Exception as e:
        print(e)


def delete_files():
    # try, except for using threading
    try:
        EntityFile.objects.filter(mediafile=None).delete()
    except Exception as e:
        print(e)


def update_quota(media_file):
    # try, except for using threading
    try:
        media_file.user.quota.update_quota_used()
    except Exception as e:
        print(e)