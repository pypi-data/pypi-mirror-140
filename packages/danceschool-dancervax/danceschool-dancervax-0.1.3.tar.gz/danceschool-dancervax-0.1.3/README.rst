DancerVax Integration for the Django Danceschool Project
========================================================

The `DancerVax <https://dancervax.org/>`_ site is designed to allow for simple
vaccination record lookup for participating organization. Lookups can happen
using the site itself, or using the included REST API.

This package provides easy DancerVax Integration to the Django Dance School
project.  Once installed, the default check in views will automatically call
the DancerVax API to check the vaccination status of potential participants at
the time of check in.  This way, vaccination checks are completely integrated
with the existing check-in workflow.

Installation instructions
-------------------------

1. Sign up as an organization with DancerVax, and await approval to begin using
   the lookup system.

2. Request a DancerVax API key (client key and secret key).

3. Install this package.::

      pip install danceschool-dancervax

   Note that in a production environment, you may need to simply add danceschool-dancervax
   to your project's requirements.txt.

4. Edit your project's settings.py to add danceschool-dancervax to INSTALLED_APPS,
   and to add your API keys::
   
      INSTALLED_APPS = [
         ''' Other packages '''
         'danceschool_dancervax',
      ]

      DANCERVAX_CLIENT_ID = '<your_id_here>'
      DANCERVAX_CLIENT_SECRET = '<your_secret_here>'

Once these steps are complete, automatic lookup of DancerVax vaccination status
should be enabled by default. On the 'View registrations' pages, each individual's
DancerVax status will be reported. The app also makes use of Django's built-in
cache capabilities; a request for information related to a specific event
registration will only be repeated once per day, unless the name or email address
associated with the registration changes.

Who do I talk to about additional questions?
--------------------------------------------

For technical questions related to this library, use the issue tracker or email
Lee Tucker: lee.c.tucker@gmail.com

For issues related to DancerVax itself, please contact info@dancervax.org.
