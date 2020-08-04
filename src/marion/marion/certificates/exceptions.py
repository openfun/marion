"""Exceptions for the marion.certificates application"""


class InvalidCertificateIssuer(Exception):
    """Invalid certificate issuer exception.

    This exception is raised when one tries to instanciate a certificate issuer
    that does not exists or is not activated in the
    CERTIFICATE_ISSUER_CHOICES_CLASS setting (see defaults).

    """


class CertificateIssuerContextQueryValidationError(Exception):
    """Certificate issuer context_query validation error.

    This exception is raised when the input context_query for a certificate
    issuer does not validate the certificate issuer context_query schema.

    """


class CertificateIssuerContextValidationError(Exception):
    """Certificate issuer context validation error.

    This exception is raised when the context fetched by a certificate issuer
    does not validate the certificate issuer context schema.

    """


class CertificateIssuerMissingContext(Exception):
    """Certificate issuer missing context error.

    This exception is raised when the certificate issuer context is missing to
    perform an action, e.g. to create a certificate.

    """
