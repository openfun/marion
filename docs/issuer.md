# Create an issuer

Once Marion is installed, you will need to create one issuer per document type
you need to generate. Your issuers should stand in a python module that bundles
templates and the business logic required to build your documents. This module
can be distributed as a python package or a core Django application in your
Django project.

## Module tree

An example `shop` module tree follows:

```
apps/shop
├── defaults.py
├── __init__.py
├── issuers
│   ├── __init__.py
│   └── invoice.py
├── static
│   └── shop
│       └── logo.svg
├── templates
│   └── shop
│       ├── invoice.css
│       └── invoice.html
└── tests
    └── issuers
        ├── __init__.py
        └── test_invoice.py
```

As you may have noticed if you are familiar with Django: the module tree looks
like a standard Django app (but without models, views and urls). Except for
the `static/{{ application_name }}` directory, the project tree is only a
recommendation, feel free to organize things the way you like.

In the proposed project tree:

- `defaults.py` contains default values to configure your issuer,
- `issuers` module contains issuers (one file per issuer),
- `static/{{ application_name }}` is the place to store images that will be
  embedded in your rendered documents,
- `templates/{{ application_name }}` contains your HTML and CSS templates that
  will be used to generate your documents, and,
- `tests/issuers` directory will ship tests for your issuers (business logic).

## Business logic

Now that your project tree is ready, you will need to write code for your
`Invoice` issuer. Before writing code, we will have to explain a key concept in
Marion's design: an issuer uses a _context query_ to fetch a _context_ that
will be used to substitute variables in your templates. In other words, this
context query is a collection of key-values that is required to build or fetch
a collection of key-values that will serve as the context.

An example issuer code follows (it will be commented in
details later):

```python
# apps/shop/issuers/invoice.py

import json

from pathlib import Path
from uuid import UUID

import requests

from pydantic import BaseModel

from marion.issuers.base import AbstractDocument


class Customer(BaseModel):
   """Customer pydantic model"""

   name: str


class Invoice(BaseModel):
   """Invoice pydantic model"""

   invoice_id: UUID
   customer: Customer
   total: float


class ContextModel(BaseModel):
   """Context pydantic model"""

   invoice: Invoice


class ContextQueryModel(BaseModel):
   """Context query pydantic model"""

   order_id: UUID


class Invoice(AbstractDocument):
   """Invoice issuer"""

   keywords = ["MyShop", "invoice"]

   context_model = ContextModel
   context_query_model = ContextQueryModel

   css_template_path = Path("shop/invoice.css")
   html_template_path = Path("shop/invoice.html")

   def fetch_context(self) -> dict:
      """Write your business logic to fetch the context here"""

      response = requests.get(
         f"https://www.myshop.com/api/orders/{self.context_query.order_id}"
      )
      order = json.loads(response.json())

      return {
         "invoice": {
            "invoice_id": order.get("id"),
            "customer": {
               "name": order.get("customer").get("fullname")
            }
            "total": order.get("total")
         }
      }

   def get_title(self):
      """Generate a PDF title that depends on the context"""
      return f"Invoice ref. {self.context.invoice.invoice_id}"
```

After reading this simplified piece of code, you may have noticed that:

1. your issuer class **should** inherit from the
   `marion.issuers.base.AbstractDocument` class,
2. your issuer class **should** implement the `fetch_context` method,
3. the `fetch_context` method **should** return a dictionnary of the context
   that will be used to render your templates (more on this later),
4. you **should** define [Pydantic](https://pydantic-docs.helpmanual.io/)
   models to validate data from your context and context query,

Note that documents metadata such as the `title`, `keywords` or `authors` can
be statically set as an issuer class attribute (_e.g._ `title`) or dynamically
using the corresponding method (_e.g._ `get_title()` for the `title` attribute
in our example). For reference, see the
[`marion.issuers.base.PDFFileMetadataMixin`](./sources/issuer.md) mixin
implementation.

## Document templates

While writing our issuer class, we've taken care of the business logic to
collect all required information (context variables) that will be integrated to
the issuer document template. The second step is to implement the logical
structure (HTML) and the design (CSS) of our document.

While writing your document template, you must keep in mind that you are
designing a printed document, _e.g._ writing CSS rules for the `print` media.

You should also note that both your HTML and CSS files are Django templates
that are consequently context-aware and versatile.

Simplified example template files for the `Invoice` issuer are presented below.

```htmldjango
<!-- apps/shop/templates/shop/invoice.html -->

{% load i18n %}
{% load static %}

<html>
  {% if debug %}
  <head>
    {{ css }}
  </head>
  {% endif %}
  <body>
    <div class="invoice">
      <header>
        <!--
            Company matters
        -->
        <div class="logo">
          <img
            src="{{ debug | yesno:",file://" }}{% static "shop/logo.svg" %}"
            alt="{% trans "company logo" %}"
          />
        </div>
      </header>
      <article class="order">
        <div class="invoice-id">
          {% trans "Invoice reference:" %} {{ invoice.invoice_id }}
        </div>
        <div class="customer">
          {{ invoice.customer.name }}
        </div>
        <div class="total-amount">
          {{ invoice.total }} &euro;
        </div>
      </article>
      <footer>
        <!--
            Contact informations
        -->
      </footer>
    </div>
  </body>
</html>
```

> If you are familiar with Django templates, `debug` blocks usage or conditions
> can be confusing at first sight. We will explain those in the next
> subsection.

```css
/* apps/shop/templates/shop/invoice.css */

/* load extra fonts */
@import url("https://fonts.googleapis.com/css2?family=Open+Sans");

body {
  font-family: "Open Sans", sans-serif;
  font-size: 11pt;
  color: #222;
}

@media print {
  /* ----------------------
   * Reset margins for media
   * ---------------------- */
  @page {
    size: A4 landscape;
    margin: 0;
    padding: 0;
  }

  body {
    padding: 0;
    background: #ffbe0b;
  }

  * {
    margin: 0;
    padding: 0;
  }

  /* ----------------------
   * Add custom styles below
   * ---------------------- */
  .invoice {
    /* [...] */
  }
}
```

### Using the document template debug view

Integrating a document template can be time consuming if you need to render it
as a PDF every time you want to check how it looks like. To ease your life,
we've cooked a template debug view that can be activated in your development
environment by modifiying your root URLs configuration as follow:

```python
# myproject.myproject.urls

from django.conf import settings

# [...]

if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("marion.urls.debug"))]
```

> We advice you not to activate this in production, it should only be active
> for development.

By using this view, you will be able to "see" your document in your browser as
a normal web page at the following URL:
[http://localhost:8000/__debug__/templates/](http://localhost:8000/__debug__/templates/)

Two GET request parameters are required to point to your template:

1. `issuer`: the target issuer path
2. `context`: the issuer context (as resulting from the issuer's
   `fetch_context` method)

A complete debug template URL example may look like:

```
http://localhost:8000/__debug__/templates/?issuer=apps.shop.issuers.invoice.Invoice&context=%7B%22invoice%22%3A+%7B%22invoice-id%22%3A+%22d972fef9%22%7D
```

Note that the JSON-serialized `context` should be URL encoded. This can be
achieved using the following python snippet:

```python
import json
import urllib.parse

with open("context.json") as example:
    print(
        urllib.parse.quote_plus(
            json.dumps(
                json.load(example)
            )
        )
    )
```

As mentionned earlier, you should keep in mind that the media that will be used
to render your document is a printer, so you should **enable print media
emulation** in the developer tools of your web browser to have a better idea of
what it will look like once rendered as a PDF.

In expected conditions (outside from a Django view context), Marion generates a
PDF file using separated HTML and CSS content. Linked files (_e.g._ embedded
images) are expected to be referenced using the `file://` protocol (a custom
url fetcher will integrate those files in the final document). But, when using
this debug view, we need to inject CSS styles in the template and serve static
files by Django to display them in the browser. This is why we add a `debug`
variable to the Django context. This variable should be used to add CSS content
in the debug view:

```htmldjango
<html>
  {% if debug %}
  <head>
    {{ css }}
  </head>
  {% endif %}

  <!-- [...] -->
</html>
```

And display images:

```htmldjango
<img
  src="{{ debug | yesno:",file://" }}{% static "shop/logo.svg" %}"
  alt="{% trans "company logo" %}"
/>
```

## Issuer configuration

Once written, we should declare distributed application issuers:

```python
# apps/shop/defaults.py

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class ShopDocumentIssuerChoices(TextChoices):
    """List active document issuers."""

    INVOICE = "apps.shop.issuers.invoice.Invoice", _("Invoice")
```

And activate them in our Django settings:

```python
# pyproject/myproject/settings.py

# Add the shop app
INSTALLED_APPS = [
    "django.contrib.admin",
    # [...]
    "rest_framework",
    "marion",
    "apps.shop",
]

# Activate shop issuers
MARION_DOCUMENT_ISSUER_CHOICES_CLASS = "apps.shop.defaults.ShopDocumentIssuerChoices"
```

Only issuers listed in the `ShopDocumentIssuerChoices` can be used in the
current Django project. If you need more issuers, you should declare them in
the `ShopDocumentIssuerChoices` enum-like object or declare a new enum listing
all allowed issuers for your project.

> Note that modifying this setting requires to create a new database migration
> as this will change choices of the `DocumentRequest.issuer` field.

## Document rendering

Once your issuer has been implemented and activated, you can generate the
corresponding PDF file using either the issuer API, the `DocumentRequest`
model or the REST API endpoint. In the first scenario, the generation of your
document will not be tracked as a document request in your database.

### Using the issuer API

To generate a document, you will need to instantiate the corresponding issuer
with an appropriate context query, and then call the `create()` method:

```python
from apps.shop.issuers.invoice.Invoice

invoice = Invoice(
   context_query={"order_id": "7866454a-600e-434a-a546-04a286b208db"}
)

# Generate the PDF file
invoice.create()
```

Your document should have been rendered in a PDF file created in the
`MARION_DOCUMENTS_ROOT` setting path. For reference, see the
[`marion.issuers.base.AbstractDocument`](./sources/issuer.md) class.


### Using the `DocumentRequest` Django model

If you want to track documents creation in your database, you should use
Marion's `DocumentRequest` model in your views:

```python
# apps/shop/views.py

from marion.models import DocumentRequest


def payment(request):
    """Payment view"""

    order_id = request.POST.get("order_id")

    invoice = DocumentRequest.objects.create(
      issuer="apps.shop.issuers.invoice.Invoice",
      context_query={"order_id": order_id}
   )

   # [...]
```

Your document should have been rendered in a PDF file created in the
`MARION_DOCUMENTS_ROOT` setting path. For reference, see the
[`marion.models.DocumentRequest`](./sources/model.md) class and the
[`marion.issuers.base.AbstractDocument`](./sources/issuer.md) class.

### Using the REST API

If you have configured Marion's urls in your project, you can use the document
request view set to get, list or create a new document:

```bash
# Create a new document using the invoice issuer
$ http POST http://localhost:8000/api/documents/requests/ \
    issuer="apps.shop.issuers.invoice.Invoice" \
    context_query='{"order_id": "7866454a-600e-434a-a546-04a286b208db"}'
```

You should have a `HTTP 200 OK` response. Yatta!

![Yatta](https://media.giphy.com/media/x2z9nswqAfpp6/giphy.gif)

Once created, check the document request ID (and the corresponding document) by
listing created objects _via_:

```bash
$ http GET http://localhost:8000/api/documents/requests/
```

## Issuer testing

Don't forget to test your business logic implemented in the `fetch_context`
method of your issuer. We use pytest along with
[hypothesis](https://hypothesis.readthedocs.io/en/latest/) as it has builtin
support for [Pydantic](https://pydantic-docs.helpmanual.io/) models.
