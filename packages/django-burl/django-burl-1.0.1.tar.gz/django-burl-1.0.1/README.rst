###########
django-burl
###########

``django-burl`` (brief url) is a URL shortening application for inclusion in
django projects. It provides a data model and a simple REST API in addition
to URL redirection capabilities.

If you are looking for a standalone URL shortener that you can quickly run in
a container, *see* `burl <https://github.com/wryfi/burl>`_ for a ready-to-go
reference implementation of ``django-burl``.


Quick Start
===========

1. Install by running ``pip install django-burl`` in your python/django environment

2. Configure ``INSTALLED_APPS`` with ``django_burl``, ``django_filter``, and ``sites``, as follows: ::

    INSTALLED_APPS = [
        ...,
        "django.contrib.sites",
        "django_filter",
        "django_burl",
    ]

3. Enable the sites midleware: ::

    MIDDLEWARE = [
        ...,
        "django.contrib.sites.middleware.CurrentSiteMiddleware"
    ]

4. Run database migrations, e.g. ``manage.py migrate``.

5. Add the URLs from ``django_burl.api.urls_v1``  or ``django_burl.urls`` to your application's URL structure.

6. Create some Brief URLs in the Django admin (logged in as a superuser).

7. Explore the API. Its URL may vary depending on how you configured your
   project. (HINT: install ``django_extensions`` and then run ``manage.py show_urls``
   to get a full list of your project's URLs if you're not sure.)


Sites & Permissions
===================

``django-burl`` uses the django sites framework, allowing you to host multiple domains under the
same django instance. Permissions to each site are determined by ``BriefURLDomainUser`` objects,
which you can create and manipulate in the Django Admin (as a superuser).

These objects map a user to a site and one of three roles:

* Creator - has the ability to create burls, and to view, modify and delete his/her own burls
* Editor - has creator permissions plus ability to view all burls and modify any burl
* Admin - has editor permissions plus ability to delete a burl

NOTE: Only superusers can change the user or site of a burl.

API requests are scoped by site. For example, if you have two sites with domains
``my.to`` and ``go.to``, you cannot manipulate the burls for ``my.to`` by making
requests to the API at http://go.to; you can only do so through http://my.to, even
though both domains are hosted on the same Django instance.


Django Admin
============

Burls can be managed by non-superusers in the Django admin, by first giving the user
"Staff status," and then giving the user the following User permissions:

* ``django_burl | brief url | Can view brief url``

The default redirect for a domain can also be managed (by a site admin) in the
django admin by granting:

* ``django_burl | brief url default redirect | Can view brief url default redirect``

This is not currently used by default, but can be used upstream as desired.

API v2 Reference
================

It is assumed that ``django-burl`` will be installed within a larger Django project,
and leaves to the project architect the task of integrating it with other API
endpoints and documentation (like swagger).

Brief URLs are represented as JSON objects of the following schema: ::

    {
        "burl": string,
        "url": string,
        "user": int | uuid,
        "description": string,
        "enabled": bool
    }

The following URL endpoints are provided: ::

    /burls (GET, POST, HEAD, OPTIONS)

        GET - list Brief URLs
        POST - create a new Brief URL (JSON body per schema above)

    /burls/<burl> (GET, PUT, PATCH, DELETE, HEAD, OPTIONS)

        GET - return details about the requested Brief URL
        PUT - entirely replace the requested Brief URL (JSON body per schema above)
        PATCH - update the provided fields on the requested Brief URL (JSON body per schema above)
        DELETE - delete the requested Brief URL


Implementation
==============

``django-burl`` implements a URL shortening service by allowing authorized users
to create a brief URL pointing to any other URL.  When creating a brief URL,
the user may specify the brief url, which must be globally unique, or the
system will generate a random one.

When the brief URL is subsequently requested from ``django-burl``, it returns
a redirect to the original URL.

There are two primary interfaces to burl:

#. the built-in django admin at ``/admin``;
#. a minimal restful API based on django rest framework.

New brief URLs can only be created by authenticated users (via session auth
or token auth by default).

``django-burl`` uses `hashids <https://hashids.org/>`_ for automatically generated
brief URLs. Each auto-generated BURL is created using a random salt and a
random number passed into the hashids library. This value is then stored in the
database. The random BURLs generated in this manner should be sufficiently
difficult to reverse engineer.


Requirements
============

code
----

You will need an existing `Django <https://www.djangoproject.com>`_
project, running at least django 2.2+ and python 3.7+.

In addition, the `sites framework <https://docs.djangoproject.com/en/4.0/ref/contrib/sites>`_
must be installed, and ``CurrentSiteMiddleware`` enabled in your project.

For a standalone url shortener implementing ``django-burl``, see
`burl <https://github.com/wryfi/burl>`_.


database
--------

A PostgreSQL database is recommended for your ``django-burl`` project.
While MySQL variants may also work, ``django-burl`` is tested against and
optimized for postgres.

Note that ``django-burl`` does rely on strong constraints, so sqlite is not
supported.

Follow the standard Django docs for configuring your database engine.


user model
----------

``django-burl`` serializes the user id field in API responses. This imposes
some limitations on the user model that can be used with the package. Namely,
your user model must have an ``id`` field that is either:

- an integer, e.g. ``AutoField`` (as found on the default django user model),
  ``BigAutoField``, or ``IntegerField``
- or a UUID, e.g. ``UUIDField``

User models that do not conform to the above specification are not supported.


Installation
============

``django-burl`` is made to be installed via the standard python installation methods.
You can install it as simply as running::

    pip install django-burl

It is recommended, of course, that you use ``django-burl`` in a virtualenv or
Docker container.

Then, configure ``INSTALLED_APPS`` and ``MIDDLEWARE`` in your ``settings.py``
as follows: ::

    INSTALLED_APPS = [
        ...,
        "django.contrib.sites",
        "django_filter",
        "django_burl",
    ]

    MIDDLEWARE = [
        ...,
        "django.contrib.sites.middleware.CurrentSiteMiddleware"
    ]

Next, run the database migrations to create the necessary tables, using your
project's management script::

    manage.py migrate

You should now see the database tables in the django admin after restarting
your application.

Finally, configure API routes by including ``django_burl.urls`` in your application's
URL configuration.

Configuration
=============

``django-burl`` reads its configuration from the django settings module. Some of the more relevant
settings may include: ::

    # list of words/letter combinations that cannot be used as brief URLs
    # do not remove the default items below, but feel free to extend and add your own
    BURL_BLACKLIST = ["admin", "api", "static", "media"]

    # an obscure setting related to estimating the # of BURLs in the django admin
    ROUGH_COUNT_MIN = 1000

    # the configured user model (must have an id that is an int or a uuid)
    AUTH_USER_MODEL = "myapp.models.user"

    # the characters available for generating BURLs
    HASHID_ALPHABET = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ0123456789"

    # number of API results per page
    API_PAGE_SIZE = 20

    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.TokenAuthentication",
        ),
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
        "PAGE_SIZE": API_PAGE_SIZE,
        "DEFAULT_PARSER_CLASSES": [
            "rest_framework.parsers.JSONParser",
        ],
        "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    }

