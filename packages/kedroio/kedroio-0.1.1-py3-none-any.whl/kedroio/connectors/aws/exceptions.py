class S3ObjectNotFound(Exception):
    pass


class CredentialsExpired(Exception):
    pass


class AthenaQueryFailed(Exception):
    pass


class AthenaQueryParameters(Exception):
    pass
