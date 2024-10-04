class ClientError(Exception):
    """
    Base class for all client errors.
    """


class ServerError(Exception):
    """
    Base class for all server errors.
    """


class ClientTimeoutError(ClientError):
    """
    Client timeout error.
    """


class ClientConnectionError(ClientError):
    """
    Client connection error.
    """


class ClientNameError(ClientError):
    """
    Client name error.
    """


class ServerBoardcastError(ServerError):
    """
    Server broadcast error.
    """
