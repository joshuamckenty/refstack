RefStack
========

Vendor-facing API for registration of interop-compliance endpoints and credentials for on-demand testing.

See (living) documentation at https://etherpad.openstack.org/RefStackBlueprint


Okay, I'm Sold, How Do I Run This Myself?
-----------------------------------------

This is our documentation for how we get this set up::

  # Git you clonin'
  git clone http://github.com/stackforge/refstack

  cd refstack

  # Setup or update the database
  # NOTE: you are going to have to modify the db connection string in
  #       `alembic.ini` to get this working
  # PROTIP: if you just want to test this out, use `-n alembic_sqlite` to
  #         make a local sqlite db
  #         $ alembic -n alembic_sqlite upgrade head

  alembic upgrade head

  # Plug this bad boy into your server infrastructure.
  # We use nginx and gunicorn, you may use something else if you are smarter
  # than we are.
  # For the most basic setup that you can try right now, just kick off
  # gunicorn:
  gunicorn -b 0.0.0.0:8000 refstack.web:app

  # To actually configure this winner, check out the config section and
  # crack open refstack.cfg in vim.
  # `vim refstack.cfg`

  # Now browse to http://localhost:8000

Project Info
============
Web-site: http://refstack.org
Source Code: http://github.com/stackforge/refstack
Wiki: https://wiki.openstack.org/wiki/RefStack
Launchpad: https://launchpad.net/refstack
Blueprints: https://blueprints.launchpad.net/refstack
Bugs: https://bugs.launchpad.net/refstack
Code Reviews: https://review.openstack.org/#q,status:open+refstack,n,z
IRC: #refstack at freenode
