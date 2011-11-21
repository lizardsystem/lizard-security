Protecting and filtering your website with lizard-security
==========================================================


What lizard-security does
-------------------------

Lizard-security is the base for all data related security in "Lizard" Django
websites:

- **Base** because every Django model must inherit from an abstract model that
  lizard-security provides. This is quite invasive, but there's no real handy
  way around it.

- **Data related** because lizard-security provides row level security. It
  works mostly on the database level.

- **Lizard** because introduces a *data set* model that you can use to group
  your data. Those groups are what you give permission to. This is a pretty
  big assumption that won't work for every site. It is exactly what we need
  for the ``lizard-*`` family of Django applications, though. Even so,
  lizard-security will also work fine for many other sites.

- **Lizard** also means that it is user friendly and that non-admins can
  configure it.

- **Django** because lizard-security tries to use Django's database models,
  Django's row level security mechanism, Django's admin filtering, Django's
  permission infrastructure. A good Django citizen.


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

- **User group**. Next to Django's *permission groups*, lizard-security
  provides user groups. A user group is, as the name says, a group of
  users. There are two kinds of users inside a group: regular members and
  managers. Managers can add and remove members from the group.

  We can assign user groups to a *permission group* in combination with a link
  to a *data set*. This means that the user group has the assigned permissions
  on the data that belongs to that *data set*. This mechanism is
  lizard-security's core.

- **Data set**. A data set is a small model in the database. Its important
  property is that other models can have a foreign key to it. This way, those
  other model instances can indicate that they belong to the data set.

  Data sets are used for filtering, based on a Django permission. You have
  a permission on something:

  - if that something is a member of a data set

  - if that dataset is assigned the permission you want

  - if you are a member of the *user group* that is attached to the data set.

