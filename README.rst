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

- **Django** because lizard-security tries to use Django's database model
  managers, Django's row level security mechanism, Django's admin filtering,
  Django's permission infrastructure. A good Django citizen.


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


Important parts 3: custom model manager that filters
----------------------------------------------------

Lizard-security provides a custom model manager that does one extra thing: it
filters models with a ``data_set`` foreign key to lizard-security's
``DataSet`` model.

- Models with an empty data set are available to all.

- Models with a data set are only accessible to users with those data set IDs
  in the request. Those IDs are normally set by our middleware.


Important parts 4: permission handling
--------------------------------------

Lizard-security does not handle global permissions. By design, it only handles
object permissions. It has ``has_perm()`` integration, so we can use the
regular Django permission calls.

If we only want to know if we can access an object, we can use
lizard-security's view permission to ask for that
``lizard_security.can_view_lizard_data``.

The permission handling is done by an authentication backend; which must be
enabled in our settings::

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'lizard_security.backends.LizardPermissionBackend',)



Important parts 5: admin middleware
-----------------------------------

The objects we're allowed to see are already filtered by our custom model
manager, so the admin middleware doesn't need to filter those.

However, often managers won't have global access to data, but only within
certain datasets. The admin middleware gives them access to the admin
interface; Django's default admin only looks at global permissions and we also
take the *permission mappers* into account.


Usage in our project
---------------------

If we have any app in our project that uses lizard-security, we need to add
the two middleware classes (SecurityMiddleware and TLSRequestMiddleware) at
the bottom of ``MIDDLEWARE_CLASSES`` in our ``settings.py``::

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

Lizard-security's permission backend needs to be enabled in our
``settings.py``::

    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'lizard_security.backends.LizardPermissionBackend',)

Any models of ours that we want to protect with lizard-security's *data set*
mechanism needs four changes:

- A ``data_set`` foreign key is needed to be able to say which *data set* the
  objects belong to.

- We need to tell Django we support object permissions.

- Lizard-security's special object manager must be set to gain the extra
  filtering (for using geo object manager in combination with lizard-security
  use FilteredGeoManager)

- We want to use (or subclass) lizard-security's special admin class.

Example usage
-------------

Here's an example illustrating the use of lizard-security. Remember to
put lizard-security in your INSTALLED_APPS list, above the apps that
use lizard-security.

    from django.db import models
    from django.contrib import admin

    from lizard_security.manager import FilteredManager
    from lizard_security.models import DataSet
    from lizard_security.admin import SecurityFilteredAdmin


    class Something(models.Model):
        supports_object_permissions = True
        data_set = models.ForeignKey(DataSet,
                                     null=True,
                                     blank=True)
        objects = FilteredManager()


    admin.site.register(Something, SecurityFilteredAdmin)

Example usage of the filtered Something::

- Add a permission group (Auth.Group) named "edit-something" and add permissions
  add, change, delete of the model Something.

- Add a user "editor" (Auth.User) and make sure the checkbox "staff"
  is checked. With the staff status you can log in to the admin
  interface with this user.

- Make a data set (lizard_security.DataSet), named "Editable".

- Make a user group (lizard_security.UserGroup), named "all editors"
  and add "editor" to the list of managers.

- Make an entry in the permission mapper
  (lizard_security.PermissionMapper) for the user group "all editors",
  the data set "Editable", the permission group "edit-something" and
  give it the name "Something Editable".

Results if you log in as editor::

- A call to Something.objects.all() will return all objects where data
  set is "Editable" and where no data set is defined. Note that if you
  empty the permission group "edit-something", you will still get the
  same result. This is because a member in the permission mapper
  automatically gets the view permission.

- If you go to the admin screen you will see the same. Note that if
  you empty the permission group, you will not see anything in the
  admin screen. The admin screen has extra filtering on model class
  which depend on the permission group.

- If you try to save an object, you must have the add/change
  permission.

- If you are not logged in, you will not see items of data set
  "Editable".


Development on lizard-security
------------------------------

Lizard-security must be solid as a rock. Therefore I've kept the **code
coverage at 100%**. If you develop on lizard-security, **keep** the coverage
at 100%.

We need to be quite conservative at adding features or corner case tweaks. If
you add one: do it in a branch. We're using Git for a reason.

Lizard-security is available `on github
<https://github.com/lizardsystem/lizard-security>`_. This is also where you
can `report bugs or suggestions
<https://github.com/lizardsystem/lizard-security/issues>`_.

The documentation is online at
http://doc.lizardsystem.nl/libs/lizard-security/ .
