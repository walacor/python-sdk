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

from walacor_sdk.utils.exceptions import (
    APIConnectionError,
    BadRequestError,
    InternalServerError,
)

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
                status = response.status_code

                content = (
                    response.content.decode("utf-8")
                    if isinstance(response.content, bytes | bytearray)
                    else str(response.content)
                )

                error_reason = "UnknownReason"
                error_message = "Unknown error message."

                try:
                    maybe_json = json.loads(content)
                    if isinstance(maybe_json, dict):
                        errors = maybe_json.get("errors", [{}])
                        first = errors[0] if errors else {}
                        if isinstance(first, dict):
                            error_reason = first.get("reason", error_reason)
                            error_message = first.get("message", error_message)
                except json.JSONDecodeError:
                    pass

                if status == 400:
                    raise BadRequestError(error_reason, error_message, status) from None

                if status == 500:
                    raise InternalServerError(
                        error_reason,
                        error_message,
                        status,
                    ) from None

                logging.error(
                    "Unhandled HTTP error: %s %s",
                    status,
                    response.reason,
                )
                raise APIConnectionError(
                    f"HTTP Error {status}: {response.reason}"
                ) from None

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
