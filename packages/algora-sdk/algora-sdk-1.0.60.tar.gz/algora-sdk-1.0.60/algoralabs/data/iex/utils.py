from algoralabs.common.requests import __get_request


def __base_request(extension: str, **kwargs):
    """
    Base GET request for IEX

    :param extension: URI extension
    :param kwargs: request query params
    :return: response
    """
    endpoint = f"data/datasets/query/iex/{extension}"
    return __get_request(endpoint=endpoint, params=kwargs)
