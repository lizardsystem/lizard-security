Protecting and filtering your website with lizard-security
==========================================================


What lizard-security does
-------------------------

Lizard-security is the base for all data related security in "Lizard" Django
websites:

- **Base** because every Django model that wants to be protected by
  lizard-security must include a foreign key to lizard-security's ``DataSet``
  model. This is quite invasive, but there's no real handy way around it.

- **Data related** because lizard-security provides row level security. It
  works mostly on the database level.

- **Lizard** because introduces a *data set* model that you can use to group
  your data. Those *data sets* are what you give permission to. This is a
  pretty big assumption that won't work for every site. It is exactly what we
  need for the ``lizard-*`` family of Django applications, though. Even so,
  lizard-security will also work fine for many other sites.

- **Lizard** also means that it is user friendly and that non-admins can
  configure it.

- **Django** because lizard-security tries to use Django's database models,
  Django's row level security mechanism, Django's admin filtering, Django's
  permission infrastructure. A good Django citizen. Oh, and because it `monkey
  patches <http://en.wikipedia.org/wiki/Monkey_patch>`_ Django's default model
  manager's ``get_query_set()`` method.


Defining terms
--------------

To get us on the same page, we'll first define some terms. It is way too easy
to get confused over the term *group*, for instance: is it a group of
permissions or is it a group of users? So here are the terms:

- **Group**. We don't use this term on its own. See *permission group*.

- **Permission group**. This is what we get as *group* from stock Django. We
  get permissions and groups: permissions can be grouped in a permission group
  in the Django admin. It gets confusing as we can assign users to both
  permissions and permission groups. This behaviour makes it look like a
  permission group is also a group of users.

  For example, we can create a permission group "cms editors" and group the
  cms-related permissions in it. And assign couple of users to that permission
  group. So... is it a group of permissions or users? Or both?

  An important point is that assigning permissions (or permission groups) to
  users means assigning *global* permissions. So we cannot group users that
  can only access one part of the site and not another. Or we'd need sparate
  permissions like ``view_north_data``, ``view_east_data``...

  For our purpose, we'll treat Django's groups as a permission group, not as a
  group of users. See the next term, *user group*.

- **User group**. Next to Django's *permission groups*, lizard-security
  provides user groups. A user group is, as the name says, a group of
  users. There are two kinds of users inside a group: regular members and
  managers. Managers can add and remove members from the group.

- **Permission mapper**. We can assign *user groups* to a *permission group*
  in combination with a link to a *data set*. This means that the *user group*
  has the assigned permissions on the data that belongs to that *data
  set*. This mechanism is lizard-security's core.

- **Data set**. A data set is a small model in the database. Its important
  property is that other models can have a foreign key to it. This way, those
  other model instances can indicate that they belong to the data set.

  Data sets are used for filtering, based on a Django permission. You have
  a permission on something:

  - if that something has a foreign key link to a data set

  - if that data set is assigned the permission you want

  - if you are a member of the *user group* that is attached to the data set.


Important parts 1: *user group*
-------------------------------

*User groups* are a relative separate part of lizard-security. As admin, we
can add *user groups* in the admin interface. We then have to assign one or
more users as manager of the *user group*.

We must allow the managers to go to the admin interface by giving them staff
status and giving them edit rights on *user groups*. The admin interface
automatically only shows the *user groups* that such a user is manager of.

A *user group* manager can add and remove regular members.


Important parts 2: middleware
-----------------------------

To use lizard-security, we need to add two middleware classes to our
``settings.py``:

- ``tls.TLSRequestMiddleware`` from `django-tls
  <https://github.com/aino/django-tls>`_. (Lizard-security depends on
  django-tls, so the Python package gets installed automatically). Django-tls
  places the request object in a so-called thread local storage, making the
  request available to Django's model layer without passing it around manually
  (which often isn't possible or practicable).

- ``lizard_security.middleware.SecurityMiddleware`` that we provide
  ourselves. Our security middleware stores *user group* membership
  information in the request. And it determines the *data sets* we have access
  to and stores that information in the request, too.

We **must** place lizard-security's middleware **below** Django's
AuthenticationMiddleware as we need the login data to do our work. Here's an
example setting::

    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'lizard_security.middleware.SecurityMiddleware',
        'tls.TLSRequestMiddleware',
        )


Important parts 3: monkey patched default queryset
--------------------------------------------------

Lizard-security does one rude thing: it replaces (via a so-called "monkey
patch") the default ``get_query_set()`` method of Django's default model
manager. The replacement does nothing unless we've registered some filters.

Filters that we register get to modify the query set before anyone sees it. So
if we call ``Something.objects.all()``, the objects are already filtered.

By default, our own filter is registered. If needed, the filters can be
configured in our settings. The default is::

    LIZARD_SECURITY_FILTERS = [
        'lizard_security.filters.data_set_filter']

Our ``data_set_filter`` filters models with a ``data_set`` foreign key to
lizard-security's ``DataSet`` model. It leaves other models alone.

- Models with an empty data set are available to all.

- Models with a data set are only accessible to users with those data set IDs
  in the request. Those IDs are normally set by our middleware.


Important parts 4: permission handling
--------------------------------------

Lizard-security does not handle global permissions. By design, it only handles
object permissions. It has ``has_perm()`` integration, so we can use the
regular Django permission calls.

