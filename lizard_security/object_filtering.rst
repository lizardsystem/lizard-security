.. -*- doctest -*-

Filtering objects through a custom object manager
=================================================


Setup
-----

Add four content objects. We use a content object that uses lizard-security's
data set as a mechanism to filter itself:

    >>> from lizard_security.testcontent.models import Content
    >>> content1 = Content(name='content1')
    >>> content1.save()
    >>> content2 = Content(name='content2')
    >>> content2.save()
    >>> content3 = Content(name='content3')
    >>> content3.save()
    >>> content4 = Content(name='content4')
    >>> content4.save()

We haven't done anything special yet and we have no request, so we get all
four objects:

    >>> len(Content.objects.all())
    4


Basic filtering through the custom model manager
------------------------------------------------

If we attach one of the content objects to a data set, we get all four
objects back as we don't have a request which could indirectly give us access
to that data set to dump and load data from command line.

    >>> from lizard_security.models import DataSet
    >>> dataset1 = DataSet(name='dataset1')
    >>> dataset1.save()
    >>> content1.data_set = dataset1
    >>> content1.save()
    >>> len(Content.objects.all())
    4


Filtering including request
---------------------------

We need to know which dataset we've got access to. This can be filtered out of
our request via our login data via a user group, for instance. But it can also
be set automatically via some middleware through IP address lookups.

Assumption for now: something set a list of data set ids we're allowed to see
in the request.

To have the request available on the model layer, we need to use `django-tls
<http://pypi.python.org/pypi/django-tls>`_. This grabs the request from the
current thread local if it enabled via middleware. We can however set a
request object by monkeypatching the request object used by our custom
manager...:

    >>> import lizard_security.manager
    >>> orig_request = lizard_security.manager.request
    >>> from mock import Mock
    >>> request = Mock()
    >>> request.allowed_data_set_ids = [dataset1.id]
    >>> request.user = None
    >>> lizard_security.manager.request = request
    >>> len(Content.objects.all())
    4

Regular user without data set ids:

    >>> request = Mock()
    >>> request.user.is_superuser = False
    >>> request.allowed_data_set_ids = []
    >>> lizard_security.manager.request = request
    >>> len(Content.objects.all())
    3

If we're a superuser we can get access to everything:

    >>> request = Mock()
    >>> request.user.is_superuser = True
    >>> request.allowed_data_set_ids = []
    >>> lizard_security.manager.request = request
    >>> len(Content.objects.all())
    4


Test cleanup:

    >>> lizard_security.manager.request = orig_request
