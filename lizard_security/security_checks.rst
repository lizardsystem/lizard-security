.. -*- doctest -*-

Security checks that lizard-security provides
=============================================

Lizard-security provides three kinds of security checks:

- We override Django's default model object manager ("``.objects.all()``")
  and filter out objects you're not allowed to see.

- In the admin site, a special model admin filters objects so that only the
  ones you are allowed to see are visible.

- A permission checker ("``has_perm()``") takes into account lizard-security's
  way of filtering.



Some things to check:

- perm checker for any permission(group), but that includes our VIEW perm.

- Model filtering (effectively: VIEW perm check). No dataset: outside of our
  perm checks, so allowed.

- Add setting PERM_DEBUG for extra logging.

- Check the speed! Look at caching!


- Dataset as separate implementation? Perhaps fews wants its own mechanism or
  automatic configured filtering.


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


Basic filtering through the default Django model manager
--------------------------------------------------------

Enable our data set filter function:

    >>> from lizard_security.filters import data_set_filter
    >>> from lizard_security import filter_registry
    >>> filter_registry.register(data_set_filter)

If we attach one of the content objects to a data set, we get only three
objects back as we don't have a request which could indirectly give us access
to that data set.

    >>> from lizard_security.models import DataSet
    >>> dataset1 = DataSet(name='dataset1')
    >>> dataset1.save()
    >>> content1.data_set = dataset1
    >>> content1.save()
    >>> len(Content.objects.all())
    3


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
request object by monkeypatching our filter...:

    >>> import lizard_security.filters
    >>> orig_request = lizard_security.filters.request
    >>> from mock import Mock
    >>> request = Mock()
    >>> request.data_set_ids = [dataset1.id]
    >>> request.user = None
    >>> lizard_security.filters.request = request
    >>> len(Content.objects.all())
    4

Regular user without data set ids:

    >>> request = Mock()
    >>> request.user.is_superuser = False
    >>> request.data_set_ids = []
    >>> lizard_security.filters.request = request
    >>> len(Content.objects.all())
    3

If we're a superuser we can get access to everything:

    >>> request = Mock()
    >>> request.user.is_superuser = True
    >>> request.data_set_ids = []
    >>> lizard_security.filters.request = request
    >>> len(Content.objects.all())
    4


Cleanup
-------

    >>> lizard_security.filters.request = orig_request
