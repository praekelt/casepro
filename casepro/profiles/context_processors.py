from __future__ import absolute_import, unicode_literals


def user(request):
    """
    Context processor that adds boolean of whether current user is an admin for current org
    """
    if request.user.is_anonymous() or not request.org:
        is_admin = False
        partner = None
    else:
        is_admin = request.user.can_administer(request.org)
        partner = request.user.get_partner(request.org)

    return {
        'user_is_admin': is_admin,
        'user_partner': partner
    }


def user_must_reply_with_faq(request):
    """
    Context processor that adds boolean of whether current user must use a pre-approved reply
    for responding to a message
    """
    must_use_faq = request.org and not request.user.is_anonymous() and request.user.must_use_faq()

    return {'user_must_reply_with_faq': must_use_faq}
