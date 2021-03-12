# Introduction

Marion is a documents factory backend to generate PDF files using a REST API
and HTML/CSS templates.

## Key concepts

Marion is a [Django](https://www.djangoproject.com/) application that can be
integrated to your Django project or deployed to production as a standalone
service.

To generate PDF files with styles, first, you will have to write your own
document **issuer** and related HTML/CSS templates in a Django application
package. Once your issuer has been installed and configured, you can create a
**document request** using the backend API with your favorite HTTP client (we ❤️
[`http`](https://httpie.io/), but `curl` is perfectly fine 😉):

```bash
# Create a new document using the dummy issuer
$ http POST http://localhost:8000/api/documents/requests/ \
    issuer="marion.certificates.issuers.DummyDocument" \
    context_query='{"fullname": "John Doe"}'
```

As you may have noticed, you should provide two parameters for this request:

1. the document `issuer` for this request (as a python module path), and,
2. a `context_query` that will be used by the issuer to resolve the **context**
   that will be injected in your HTML/CSS templates to generate a document;
   think of a context as a [Django template
   context](https://docs.djangoproject.com/en/3.1/topics/templates/#context).

If you get lucky, your document has been cooked. It is available for download
in the configured `MEDIA_ROOT` of the Django project Marion has been integrated
to. You will find the link to the PDF document in the newly created document
request (see the `document_url` field):

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

### Key takeways

- **Issuer**: this keyword designates a particular type of document
  with its own templates and logic to fetch a context that will be used to
  create it.
- **Document request**: a database entry tracking the context (query) used to
  generate a document and its download link.
- **Context query**: parameters that will be used by an issuer to fetch a context
  that will be used to compile a document template.
- **Context**: all variables that will be used to render document templates
  (_e.g._ a Django context).
