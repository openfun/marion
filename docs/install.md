# Installation

## Pre-requisite

Marion depends on the [Weasyprint project](https://weasyprint.org/). As such it
inherits from its core dependencies. Please make sure that you have [installed
them](https://weasyprint.readthedocs.io/en/latest/install.html) before
installing Marion.

As example, in a Debian-based distribution, you may need to install the
following packages:

```
$ (sudo) apt-get install -y \
    libcairo2 \
    libffi-dev \
    libgdk-pixbuf2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    shared-mime-info
```

## Install Marion python package

Marion is distributed as a python package. It can be installed from
[PyPI](https://pypi.org/project/django-marion/) using the `pip` tool (or any
other python package manager):

```sh
# Create a new virtualenv (optional)
$ python -m venv venv
$ source venv/bin/activate

# Install the package (in a virtualenv)
(venv) $ pip install django-marion
```

From here, you have two options: either integrate the `marion` application in
an existing Django project or create a new Django project to run Marion as a
standalone service.

## Create a standalone sandbox for Marion

> If you already have a running Django project and intend to integrate Marion
> in this project, you can safely skip this section and read the next one.

If you are starting from scratch to test Marion or prefer having a standalone
service running marion, let's create a new Django project that will be used as
a sandbox:

```bash
# Install Django
(venv) $ pip install Django

# Create a new project
(venv) $ django-admin startproject myproject
```

You have created a new Django project called `myproject`. It should look like:

```bash
myproject
├── manage.py
└── myproject
    ├── asgi.py
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py

1 directory, 6 files
```

You can now proceed with Marion's integration in the next subsection.

## Integrate Marion in a Django project

Marion's integration in your project follows a standard procedure for a Django
application:

1\. add `rest_framework` and `marion` to your installed apps:

```python
# myproject/settings.py

INSTALLED_APPS = [
    "django.contrib.admin",
    # [...]
    "rest_framework",
    "marion",
]
```

2\. add `marion` urls to your `ROOT_URLCONF` module:

```python
# myproject/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = (
    [
        path("admin/", admin.site.urls),
        # [...]
        path("api/documents/", include("marion.urls")),
    ]
    # Optionally serve static and media files when DEBUG=True
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
```

3\. run `marion`'s database migrations:

```bash
(venv) $ python manage.py migrate
```

## Create your first document

Now that Marion is configured and migrated, let's run Django's development
server to generate a document:

```bash
(venv) $ python manage.py runserver
```

If you haven't installed [`http`](https://httpie.io/) (come on, really?), you can safely test it in
your virtual environment:

```bash
(venv) $ pip install httpie
```

Perform your first document request using `http`:

```bash
(venv) $ http POST http://localhost:8000/api/documents/requests/ \
    issuer="marion.certificates.issuers.DummyDocument" \
    context_query='{"fullname": "John Doe"}'
```

If everything has been properly configured, you should have a `HTTP 200`
response to this API request. And the json response should look like:

```json
{
    "document_id": "60593260-2c0f-4c54-88e5-96ae0db06081",
    "document_url": "http://localhost:8000/media/60593260-2c0f-4c54-88e5-96ae0db06081.pdf",
    "context": {
        "fullname": "John Doe",
        "identifier": "60593260-2c0f-4c54-88e5-96ae0db06081"
    },
    "context_query": {
        "fullname": "John Doe"
    },
    "created_on": "2021-03-12T15:48:15.737311Z",
    "issuer": "marion.documents.issuers.DummyDocument",
    "updated_on": "2021-03-12T15:48:15.737336Z",
    "url": "http://localhost:8000/api/documents/requests/b90031a6-dcb4-49d6-ac6c-017030352f33/"
}
```

As you may have already guessed, your document has been properly generated and
it can be viewed/downloaded from the Django's media folder at the following
URL: `http://localhost:8000/media/60593260-2c0f-4c54-88e5-96ae0db06081.pdf`

At this stage, we have validated that Marion is properly installed and
configured. Even if the dummy document looks nice, you may ask: "Ok, now what?
How can I create custom documents that suit my needs?"

![Yoda](https://media.giphy.com/media/3ohuAxV0DfcLTxVh6w/giphy.gif)

> In the next section, answered this question will be.
