class APIServiceException(Exception):
    pass


class APIServiceUnavailableException(APIServiceException):
    pass


class APIUnauthorizedException(APIServiceException):
    pass


class TokenRequestException(APIServiceException):
    pass


class TokenRefreshException(APIServiceException):
    pass


class UserCreateException(APIServiceException):
    pass


class UserCreateDuplicateException(UserCreateException):
    pass


class UserCreateValuesException(UserCreateException):
    pass
