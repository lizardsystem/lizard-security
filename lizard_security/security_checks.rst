.. -*- doctest -*-

Security checks that lizard-security provides
=============================================

Lizard-security provides three kinds of security checks:

- A special model object manager ("``.objects.all()``") filters out objects
  you're not allowed to see. Or: we hack the default object manager to do the
  same.

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


