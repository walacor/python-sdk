from __future__ import annotations

import mimetypes
import os
import re

from io import BytesIO
from pathlib import Path
from typing import Any, cast
from urllib.parse import urljoin

import requests

from pydantic import ValidationError

from walacor_sdk.base.base_service import BaseService
from walacor_sdk.file_request.models.file_request_request import (
    StoreFileRequest,
    VerifySingleFileRequest,
)
from walacor_sdk.file_request.models.file_request_response import (
    ListFilesResponse,
    StoreFileResponse,
    VerifySuccessResponse,
)
from walacor_sdk.file_request.models.models import (
    DuplicateData,
    FileInfo,
    FileItem,
    FileMetadata,
    MemoryFileItem,
    StoreFileData,
)
from walacor_sdk.utils.exceptions import FileRequestError
from walacor_sdk.utils.logger import get_logger

logger = get_logger(__name__)


class FileRequestService(BaseService):
    # ------------------------------------------------------------------ verify
    def verify(
        self, *, file: VerifySingleFileRequest, use_progress: bool = False
    ) -> FileInfo | DuplicateData:
        """
        Upload *file* for verification and return validated ``FileInfo``.

        Args:
            file: File wrapper containing path and metadata.
            use_progress: Enable tqdm progress bar.

        Returns:
            :class:`FileInfo` metadata of the verified file.

        Raises:
            FileRequestError: On network or schema failure.
            DuplicateFileError: If the backend reports the file already exists.
        """
        logger.info("Verifying")
        is_mem = isinstance(file.file, MemoryFileItem)

        try:
            if use_progress and not is_mem:
                file_item = cast(FileItem, file.file)
                response_json = self._upload_file_with_progress(
                    path=str(file_item.path),
                    url=urljoin(self.client.base_url, "api/v2/files/verify"),
                    field_name="file",
                    mime_type=file_item.mimetype,
                )
            else:
                response_json = self._post(
                    "v2/files/verify", files=file.to_files_param()
                )

            if response_json.get("success") is True:
                parsed_success = VerifySuccessResponse(**response_json)
                return parsed_success.data.fileInfo

            if "duplicateData" in response_json:
                dup = DuplicateData(**response_json["duplicateData"])
                return dup

            raise FileRequestError("Unexpected verification response structure.")

        except (requests.RequestException, ValidationError) as exc:
            logger.exception("File verification failed")
            raise FileRequestError("verification failed") from exc

    def verify_in_memory(self, obj: Any, /, **kw: Any) -> FileInfo | DuplicateData:
        """
        Verify an in-memory pandas.DataFrame or numpy.ndarray.
        """
        if self.is_dataframe(obj):
            buf, name, mime = self.serialize_dataframe(obj, **kw)
        elif self.is_ndarray(obj):
            buf, name, mime = self.serialize_ndarray(obj, **kw)
        else:
            raise TypeError(
                "verify_in_memory() accepts pandas.DataFrame or numpy.ndarray"
            )

        item = MemoryFileItem(buf, name=name, mimetype=mime)
        request = VerifySingleFileRequest.from_memory(item)

        return self.verify(file=request, use_progress=False)

    # ------------------------------------------------------------------ store
    def store(self, *, file_info: FileInfo) -> StoreFileData:
        """
        Store a **previously verified** file into Walacor and get back UID/path refs.

        Args:
            file_info: Metadata returned from ``verify()``.

        Returns:
            :class:`StoreFileData` with UID and location metadata.

        Raises:
            FileRequestError: On API or response schema failure.
        """
        payload = StoreFileRequest(fileInfo=file_info)
        try:
            response_json = self._post(
                "v2/files/store", json=payload.model_dump(by_alias=True)
            )

            if not response_json or not response_json.get("success"):
                logger.error("File store request failed")
                raise FileRequestError("store failed")

            parsed = StoreFileResponse(**response_json)
            return parsed.data
        except (requests.RequestException, ValidationError) as exc:
            logger.exception("Storing file failed")
            raise FileRequestError("store failed") from exc

    # ------------------------------------------------------------------ download
    def download(self, *, uid: str, save_to: str | Path | None = None) -> Path:
        """
        Download the file identified by *uid* and save it locally.

        Args:
            uid: Unique identifier of the file in Walacor.
            save_to: Path or directory where file should be saved.

        Returns:
            :class:`Path` to downloaded file.

        Raises:
            FileRequestError: If metadata is missing or write fails.
        """
        logger.info("Downloading file UID=%s", uid)

        metadata = self._get_metadata(uid)
        if metadata is None:
            raise FileRequestError(f"no metadata found for UID {uid!r}")

        response = self._request_stream("download", json={"UID": uid})

        if isinstance(save_to, str | Path) and Path(save_to).suffix:
            file_path = Path(save_to).expanduser().resolve()
            save_dir = file_path.parent
            filename = file_path.name
        else:
            filename = metadata.name or self._extract_filename_from_headers(
                dict(response.headers),
                uid,
                metadata.mimetype or "application/octet-stream",
            )

            save_dir = Path(save_to) if save_to else self._default_download_dir()
            file_path = save_dir / filename

        save_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(file_path, "wb") as fp:
                for chunk in response.iter_content(chunk_size=None):
                    fp.write(chunk)
            logger.info("File saved to %s", file_path)
            return file_path
        except OSError as exc:
            logger.exception("Failed to write file to disk")
            raise FileRequestError("failed to write file") from exc

    # ------------------------------------------------------------------ list
    def list_files(
        self,
        *,
        uid: str | None = None,
        page_size: int = 0,
        page_no: int = 0,
        from_summary: bool = False,
        total_req: bool = True,
    ) -> list[FileMetadata]:
        """
        List files available in Walacor, optionally filtered by UID.

        Args:
            uid: Filter to files matching this UID.
            page_size: Records per page.
            page_no: Page index.
            from_summary: Use summarized file metadata view.
            total_req: Request total row count.

        Returns:
            List of :class:`FileMetadata` entries.

        Raises:
            FileRequestError: If request or response validation fails.
        """
        logger.info("Listing files from server")

        query = (
            f"query/get?fromSummary={str(from_summary).lower()}"
            f"&totalReq={str(total_req).lower()}"
            f"&pageSize={page_size}&pageNo={page_no}"
        )

        payload: dict[str, Any] = {"UID": uid} if uid else {}
        headers = {"ETId": "17"}

        try:
            response_json = self._post(query, json=payload, headers=headers)

            if not response_json or not response_json.get("success"):
                logger.error("List files request failed")
                raise FileRequestError("list files failed")

            parsed = ListFilesResponse(**response_json)
            logger.info("Received %s file(s)", parsed.total)
            return parsed.data
        except (requests.RequestException, ValidationError) as exc:
            logger.exception("Failed to list files")
            raise FileRequestError("list files failed") from exc

    # ------------------------------------------------------------------ helpers
    def _get_metadata(self, uid: str) -> FileMetadata | None:
        for f in self.list_files(uid=uid):
            if getattr(f, "Status", None) == "received":
                return f
        return None

    def _request_stream(self, path: str, **req_kwargs: Any) -> requests.Response:
        url_path = urljoin("v2/files/download", path)

        try:
            response = cast(
                requests.Response,
                self._post(url_path, parse_json=False, stream=True, **req_kwargs),
            )
            response.raise_for_status()
            return response
        except requests.RequestException:
            logger.exception("Streaming HTTP request to %s failed", url_path)
            raise

    @staticmethod
    def _extract_filename_from_headers(
        headers: dict[str, str], uid: str, content_type: str
    ) -> str:
        cd = headers.get("Content-Disposition", "")
        if "filename=" in cd:
            if match := re.search(r'filename="?([^"]+)"?', cd):
                return match.group(1)
        return f"{uid}{mimetypes.guess_extension(content_type) or '.bin'}"

    @staticmethod
    def _default_download_dir() -> Path:
        return (
            Path(os.getenv("XDG_DOWNLOAD_DIR", Path.home() / "Downloads")) / "walacor"
        )

    # ------------- restored upload helper -------------
    def _upload_file_with_progress(
        self,
        *,
        path: str | os.PathLike[str],
        url: str,
        field_name: str = "file",
        mime_type: str = "application/octet-stream",
    ) -> dict[str, Any]:
        from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
        from tqdm import tqdm

        file_path = Path(path)
        encoder = MultipartEncoder(
            {field_name: (file_path.name, file_path.open("rb"), mime_type)}
        )

        with tqdm(
            total=encoder.len,
            unit="B",
            unit_scale=True,
            desc=f"Uploading {file_path.name}",
        ) as bar:

            def on_upload(monitor: MultipartEncoderMonitor) -> None:
                bar.update(monitor.bytes_read - bar.n)
                if monitor.bytes_read == encoder.len:
                    bar.refresh()

            monitor = MultipartEncoderMonitor(encoder, on_upload)

            self.client.authenticate()
            headers = self.client.get_default_headers(content_type=None)
            headers["Content-Type"] = monitor.content_type

            try:
                resp = requests.post(url, data=monitor, headers=headers, timeout=120)

                if resp.status_code == 422:
                    return cast(dict[str, Any], resp.json())

                resp.raise_for_status()

                if resp.headers.get("content-type", "").startswith("application/json"):
                    return cast(dict[str, Any], resp.json())

                raise FileRequestError(
                    f"Expected JSON but server sent {resp.headers.get('content-type')}"
                )

            except requests.RequestException as exc:
                logger.exception("Upload failed")
                raise FileRequestError("upload failed") from exc

    def serialize_dataframe(
        self, df: Any, *, fmt: str = "parquet", name: str | None = None, **kw: Any
    ) -> tuple[BytesIO, str, str]:

        buf = BytesIO()
        if fmt == "csv":
            df.to_csv(buf, index=False, **kw)
            mime = "text/csv"
            filename = name or "data.csv"
        else:
            df.to_parquet(buf, **kw)
            mime = "application/x-parquet"
            filename = name or "data.parquet"
        buf.seek(0)
        return buf, filename, mime

    def serialize_ndarray(
        self, arr: Any, *, name: str = "array.npy", **kw: Any
    ) -> tuple[BytesIO, str, str]:
        try:
            import numpy as np
        except ModuleNotFoundError as err:
            raise ImportError(
                "ndarray support requires NumPy. Run:  pip install numpy"
            ) from err

        buf = BytesIO()
        np.save(buf, arr, **kw)
        buf.seek(0)
        return buf, name, "application/octet-stream"

    def is_dataframe(self, x: Any) -> bool:
        return hasattr(x, "to_parquet") and hasattr(x, "to_csv")

    def is_ndarray(self, x: Any) -> bool:
        return hasattr(x, "shape") and hasattr(x, "dtype")
