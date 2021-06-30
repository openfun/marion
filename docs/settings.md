# Settings

Marion's defaults can be overridden using the following Django settings:


* `MARION_DOCUMENT_ISSUER_CHOICES`: a list of dictionaries of avaiable 
  active issuers for your project (default: 
  `[{"issuer_path": "marion.issuers.DummyDocument", "label": "Dummy"},]`)
* `MARION_DOCUMENTS_ROOT`: the root directory that will store generated
  documents (default: `Path(settings.MEDIA_ROOT)`)
* `MARION_DOCUMENTS_TEMPLATE_ROOT`: the default relative template path where to
  find templates for your issuer (default: `Path("marion")`)
