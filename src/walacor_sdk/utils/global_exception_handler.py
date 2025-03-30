import json
import logging

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from requests.exceptions import (
    ConnectionError,
    ConnectTimeout,
    HTTPError,
    RequestException,
)

from walacor_sdk.utils.exceptions import APIConnectionError, BadRequestError

F = TypeVar("F", bound=Callable[..., Any])


def global_exception_handler(func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)

        except (ConnectTimeout, ConnectionError) as conn_err:
            logging.error("Connection error: %s", conn_err)
            raise APIConnectionError(
                "Walacor API is unreachable (connection timeout)."
            ) from None

        except HTTPError as http_err:
            response = getattr(http_err, "response", None)
            if response is not None:
                if response.status_code == 400:
                    content = (
                        response.content.decode("utf-8")
                        if isinstance(response.content, bytes)
                        else str(response.content)
                    )

                    error_data = json.loads(content)
                    error_reason = error_data.get("errors", [{}])[0].get(
                        "reason", "UnknownReason"
                    )
                    error_message = error_data.get("errors", [{}])[0].get(
                        "message", "Unknown error message."
                    )
                    raise BadRequestError(error_reason, error_message, 400) from None
                else:
                    logging.error(
                        "Unhandled HTTP error: %s %s",
                        response.status_code,
                        response.reason,
                    )
                    raise APIConnectionError(
                        f"HTTP Error {response.status_code}: {response.reason}"
                    ) from None
            else:
                logging.error("HTTPError raised without response attached.")
                raise APIConnectionError(
                    "HTTP error occurred with no response attached."
                ) from None

        except RequestException as req_err:
            logging.error("HTTP request failed: %s", req_err)
            raise APIConnectionError(
                "An HTTP error occurred while contacting Walacor API."
            ) from None

        except (BadRequestError, APIConnectionError):
            raise

        except Exception as exc:
            logging.error("Unexpected error: %s", exc)
            raise APIConnectionError(
                "An unexpected error occurred in the Walacor SDK."
            ) from None

    return cast(F, wrapper)
