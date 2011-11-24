.. -*- doctest -*-

Security checks that lizard-security provides
=============================================

Lizard-security provides three kinds of security checks:

- In the admin site, a special model admin filters objects so that only the
  ones you are allowed to see are visible.

- A permission checker ("``has_perm()``") takes into account lizard-security's
  way of filtering.

- A special model object manager ("``.objects.all()``") filters out objects
  you're not allowed to see. Or: we hack the default object manager to do the
  same.




