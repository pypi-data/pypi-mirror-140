# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Support for downloading media from Google APIs."""

import urllib3.response  # type: ignore

from google.resumable_media import _download
from google.resumable_media import common
from google.resumable_media import _helpers
from google.resumable_media.requests import _request_helpers


_CHECKSUM_MISMATCH = """\
Checksum mismatch while downloading:

  {}

The X-Goog-Hash header indicated an {checksum_type} checksum of:

  {}

but the actual {checksum_type} checksum of the downloaded contents was:

  {}
"""


class Download(_request_helpers.RequestsMixin, _download.Download):
    """Helper to manage downloading a resource from a Google API.

    "Slices" of the resource can be retrieved by specifying a range
    with ``start`` and / or ``end``. However, in typical usage, neither
    ``start`` nor ``end`` is expected to be provided.

    Args:
        media_url (str): The URL containing the media to be downloaded.
        stream (IO[bytes]): A write-able stream (i.e. file-like object) that
            the downloaded resource can be written to.
        start (int): The first byte in a range to be downloaded. If not
            provided, but ``end`` is provided, will download from the
            beginning to ``end`` of the media.
        end (int): The last byte in a range to be downloaded. If not
            provided, but ``start`` is provided, will download from the
            ``start`` to the end of the media.
        headers (Optional[Mapping[str, str]]): Extra headers that should
            be sent with the request, e.g. headers for encrypted data.
        checksum Optional([str]): The type of checksum to compute to verify
            the integrity of the object. The response headers must contain
            a checksum of the requested type. If the headers lack an
            appropriate checksum (for instance in the case of transcoded or
            ranged downloads where the remote service does not know the
            correct checksum) an INFO-level log will be emitted. Supported
            values are "md5", "crc32c" and None. The default is "md5".

    Attributes:
        media_url (str): The URL containing the media to be downloaded.
        start (Optional[int]): The first byte in a range to be downloaded.
        end (Optional[int]): The last byte in a range to be downloaded.
    """

    def _write_to_stream(self, response):
        """Write response body to a write-able stream.

        .. note:

            This method assumes that the ``_stream`` attribute is set on the
            current download.

        Args:
            response (~requests.Response): The HTTP response object.

        Raises:
            ~google.resumable_media.common.DataCorruption: If the download's
                checksum doesn't agree with server-computed checksum.
        """

        # Retrieve the expected checksum only once for the download request,
        # then compute and validate the checksum when the full download completes.
        # Retried requests are range requests, and there's no way to detect
        # data corruption for that byte range alone.
        if self._expected_checksum is None and self._checksum_object is None:
            # `_get_expected_checksum()` may return None even if a checksum was
            # requested, in which case it will emit an info log _MISSING_CHECKSUM.
            # If an invalid checksum type is specified, this will raise ValueError.
            expected_checksum, checksum_object = _helpers._get_expected_checksum(
                response, self._get_headers, self.media_url, checksum_type=self.checksum
            )
            self._expected_checksum = expected_checksum
            self._checksum_object = checksum_object
        else:
            expected_checksum = self._expected_checksum
            checksum_object = self._checksum_object

        with response:
            # NOTE: In order to handle compressed streams gracefully, we try
            # to insert our checksum object into the decompression stream. If
            # the stream is indeed compressed, this will delegate the checksum
            # object to the decoder and return a _DoNothingHash here.
            local_checksum_object = _add_decoder(response.raw, checksum_object)
            body_iter = response.iter_content(
                chunk_size=_request_helpers._SINGLE_GET_CHUNK_SIZE, decode_unicode=False
            )
            for chunk in body_iter:
                self._stream.write(chunk)
                self._bytes_downloaded += len(chunk)
                local_checksum_object.update(chunk)

        if expected_checksum is not None:
            actual_checksum = _helpers.prepare_checksum_digest(checksum_object.digest())
            if actual_checksum != expected_checksum:
                msg = _CHECKSUM_MISMATCH.format(
                    self.media_url,
                    expected_checksum,
                    actual_checksum,
                    checksum_type=self.checksum.upper(),
                )
                raise common.DataCorruption(response, msg)

    def consume(
        self,
        transport,
        timeout=(
            _request_helpers._DEFAULT_CONNECT_TIMEOUT,
            _request_helpers._DEFAULT_READ_TIMEOUT,
        ),
    ):
        """Consume the resource to be downloaded.

        If a ``stream`` is attached to this download, then the downloaded
        resource will be written to the stream.

        Args:
            transport (~requests.Session): A ``requests`` object which can
                make authenticated requests.
            timeout (Optional[Union[float, Tuple[float, float]]]):
                The number of seconds to wait for the server response.
                Depending on the retry strategy, a request may be repeated
                several times using the same timeout each time.

                Can also be passed as a tuple (connect_timeout, read_timeout).
                See :meth:`requests.Session.request` documentation for details.

        Returns:
            ~requests.Response: The HTTP response returned by ``transport``.

        Raises:
            ~google.resumable_media.common.DataCorruption: If the download's
                checksum doesn't agree with server-computed checksum.
            ValueError: If the current :class:`Download` has already
                finished.
        """
        method, _, payload, headers = self._prepare_request()
        # NOTE: We assume "payload is None" but pass it along anyway.
        request_kwargs = {
            "data": payload,
            "headers": headers,
            "timeout": timeout,
        }
        if self._stream is not None:
            request_kwargs["stream"] = True

        # Assign object generation if generation is specified in the media url.
        if self._object_generation is None:
            self._object_generation = _helpers._get_generation_from_url(self.media_url)

        # Wrap the request business logic in a function to be retried.
        def retriable_request():
            url = self.media_url

            # To restart an interrupted download, read from the offset of last byte
            # received using a range request, and set object generation query param.
            if self._bytes_downloaded > 0:
                _download.add_bytes_range(
                    self._bytes_downloaded, self.end, self._headers
                )
                request_kwargs["headers"] = self._headers

                # Set object generation query param to ensure the same object content is requested.
                if (
                    self._object_generation is not None
                    and _helpers._get_generation_from_url(self.media_url) is None
                ):
                    query_param = {"generation": self._object_generation}
                    url = _helpers.add_query_parameters(self.media_url, query_param)

            result = transport.request(method, url, **request_kwargs)

            # If a generation hasn't been specified, and this is the first response we get, let's record the
            # generation. In future requests we'll specify the generation query param to avoid data races.
            if self._object_generation is None:
                self._object_generation = _helpers._parse_generation_header(
                    result, self._get_headers
                )

            self._process_response(result)

            if self._stream is not None:
                self._write_to_stream(result)

            return result

        return _request_helpers.wait_and_retry(
            retriable_request, self._get_status_code, self._retry_strategy
        )


class RawDownload(_request_helpers.RawRequestsMixin, _download.Download):
    """Helper to manage downloading a raw resource from a Google API.

    "Slices" of the resource can be retrieved by specifying a range
    with ``start`` and / or ``end``. However, in typical usage, neither
    ``start`` nor ``end`` is expected to be provided.

    Args:
        media_url (str): The URL containing the media to be downloaded.
        stream (IO[bytes]): A write-able stream (i.e. file-like object) that
            the downloaded resource can be written to.
        start (int): The first byte in a range to be downloaded. If not
            provided, but ``end`` is provided, will download from the
            beginning to ``end`` of the media.
        end (int): The last byte in a range to be downloaded. If not
            provided, but ``start`` is provided, will download from the
            ``start`` to the end of the media.
        headers (Optional[Mapping[str, str]]): Extra headers that should
            be sent with the request, e.g. headers for encrypted data.
        checksum Optional([str]): The type of checksum to compute to verify
            the integrity of the object. The response headers must contain
            a checksum of the requested type. If the headers lack an
            appropriate checksum (for instance in the case of transcoded or
            ranged downloads where the remote service does not know the
            correct checksum) an INFO-level log will be emitted. Supported
            values are "md5", "crc32c" and None. The default is "md5".
    Attributes:
        media_url (str): The URL containing the media to be downloaded.
        start (Optional[int]): The first byte in a range to be downloaded.
        end (Optional[int]): The last byte in a range to be downloaded.
    """

    def _write_to_stream(self, response):
        """Write response body to a write-able stream.

        .. note:

            This method assumes that the ``_stream`` attribute is set on the
            current download.

        Args:
            response (~requests.Response): The HTTP response object.

        Raises:
            ~google.resumable_media.common.DataCorruption: If the download's
                checksum doesn't agree with server-computed checksum.
        """
        # Retrieve the expected checksum only once for the download request,
        # then compute and validate the checksum when the full download completes.
        # Retried requests are range requests, and there's no way to detect
        # data corruption for that byte range alone.
        if self._expected_checksum is None and self._checksum_object is None:
            # `_get_expected_checksum()` may return None even if a checksum was
            # requested, in which case it will emit an info log _MISSING_CHECKSUM.
            # If an invalid checksum type is specified, this will raise ValueError.
            expected_checksum, checksum_object = _helpers._get_expected_checksum(
                response, self._get_headers, self.media_url, checksum_type=self.checksum
            )
            self._expected_checksum = expected_checksum
            self._checksum_object = checksum_object
        else:
            expected_checksum = self._expected_checksum
            checksum_object = self._checksum_object

        with response:
            body_iter = response.raw.stream(
                _request_helpers._SINGLE_GET_CHUNK_SIZE, decode_content=False
            )
            for chunk in body_iter:
                self._stream.write(chunk)
                self._bytes_downloaded += len(chunk)
                checksum_object.update(chunk)
            response._content_consumed = True

        if expected_checksum is not None:
            actual_checksum = _helpers.prepare_checksum_digest(checksum_object.digest())

            if actual_checksum != expected_checksum:
                msg = _CHECKSUM_MISMATCH.format(
                    self.media_url,
                    expected_checksum,
                    actual_checksum,
                    checksum_type=self.checksum.upper(),
                )
                raise common.DataCorruption(response, msg)

    def consume(
        self,
        transport,
        timeout=(
            _request_helpers._DEFAULT_CONNECT_TIMEOUT,
            _request_helpers._DEFAULT_READ_TIMEOUT,
        ),
    ):
        """Consume the resource to be downloaded.

        If a ``stream`` is attached to this download, then the downloaded
        resource will be written to the stream.

        Args:
            transport (~requests.Session): A ``requests`` object which can
                make authenticated requests.
            timeout (Optional[Union[float, Tuple[float, float]]]):
                The number of seconds to wait for the server response.
                Depending on the retry strategy, a request may be repeated
                several times using the same timeout each time.

                Can also be passed as a tuple (connect_timeout, read_timeout).
                See :meth:`requests.Session.request` documentation for details.

        Returns:
            ~requests.Response: The HTTP response returned by ``transport``.

        Raises:
            ~google.resumable_media.common.DataCorruption: If the download's
                checksum doesn't agree with server-computed checksum.
            ValueError: If the current :class:`Download` has already
                finished.
        """
        method, _, payload, headers = self._prepare_request()
        # NOTE: We assume "payload is None" but pass it along anyway.
        request_kwargs = {
            "data": payload,
            "headers": headers,
            "timeout": timeout,
            "stream": True,
        }

        # Assign object generation if generation is specified in the media url.
        if self._object_generation is None:
            self._object_generation = _helpers._get_generation_from_url(self.media_url)

        # Wrap the request business logic in a function to be retried.
        def retriable_request():
            url = self.media_url

            # To restart an interrupted download, read from the offset of last byte
            # received using a range request, and set object generation query param.
            if self._bytes_downloaded > 0:
                _download.add_bytes_range(
                    self._bytes_downloaded, self.end, self._headers
                )
                request_kwargs["headers"] = self._headers

                # Set object generation query param to ensure the same object content is requested.
                if (
                    self._object_generation is not None
                    and _helpers._get_generation_from_url(self.media_url) is None
                ):
                    query_param = {"generation": self._object_generation}
                    url = _helpers.add_query_parameters(self.media_url, query_param)

            result = transport.request(method, url, **request_kwargs)

            # If a generation hasn't been specified, and this is the first response we get, let's record the
            # generation. In future requests we'll specify the generation query param to avoid data races.
            if self._object_generation is None:
                self._object_generation = _helpers._parse_generation_header(
                    result, self._get_headers
                )

            self._process_response(result)

            if self._stream is not None:
                self._write_to_stream(result)

            return result

        return _request_helpers.wait_and_retry(
            retriable_request, self._get_status_code, self._retry_strategy
        )


class ChunkedDownload(_request_helpers.RequestsMixin, _download.ChunkedDownload):
    """Download a resource in chunks from a Google API.

    Args:
        media_url (str): The URL containing the media to be downloaded.
        chunk_size (int): The number of bytes to be retrieved in each
            request.
        stream (IO[bytes]): A write-able stream (i.e. file-like object) that
            will be used to concatenate chunks of the resource as they are
            downloaded.
        start (int): The first byte in a range to be downloaded. If not
            provided, defaults to ``0``.
        end (int): The last byte in a range to be downloaded. If not
            provided, will download to the end of the media.
        headers (Optional[Mapping[str, str]]): Extra headers that should
            be sent with each request, e.g. headers for data encryption
            key headers.

    Attributes:
        media_url (str): The URL containing the media to be downloaded.
        start (Optional[int]): The first byte in a range to be downloaded.
        end (Optional[int]): The last byte in a range to be downloaded.
        chunk_size (int): The number of bytes to be retrieved in each request.

    Raises:
        ValueError: If ``start`` is negative.
    """

    def consume_next_chunk(
        self,
        transport,
        timeout=(
            _request_helpers._DEFAULT_CONNECT_TIMEOUT,
            _request_helpers._DEFAULT_READ_TIMEOUT,
        ),
    ):
        """Consume the next chunk of the resource to be downloaded.

        Args:
            transport (~requests.Session): A ``requests`` object which can
                make authenticated requests.
            timeout (Optional[Union[float, Tuple[float, float]]]):
                The number of seconds to wait for the server response.
                Depending on the retry strategy, a request may be repeated
                several times using the same timeout each time.

                Can also be passed as a tuple (connect_timeout, read_timeout).
                See :meth:`requests.Session.request` documentation for details.

        Returns:
            ~requests.Response: The HTTP response returned by ``transport``.

        Raises:
            ValueError: If the current download has finished.
        """
        method, url, payload, headers = self._prepare_request()

        # Wrap the request business logic in a function to be retried.
        def retriable_request():
            # NOTE: We assume "payload is None" but pass it along anyway.
            result = transport.request(
                method,
                url,
                data=payload,
                headers=headers,
                timeout=timeout,
            )
            self._process_response(result)
            return result

        return _request_helpers.wait_and_retry(
            retriable_request, self._get_status_code, self._retry_strategy
        )


class RawChunkedDownload(_request_helpers.RawRequestsMixin, _download.ChunkedDownload):
    """Download a raw resource in chunks from a Google API.

    Args:
        media_url (str): The URL containing the media to be downloaded.
        chunk_size (int): The number of bytes to be retrieved in each
            request.
        stream (IO[bytes]): A write-able stream (i.e. file-like object) that
            will be used to concatenate chunks of the resource as they are
            downloaded.
        start (int): The first byte in a range to be downloaded. If not
            provided, defaults to ``0``.
        end (int): The last byte in a range to be downloaded. If not
            provided, will download to the end of the media.
        headers (Optional[Mapping[str, str]]): Extra headers that should
            be sent with each request, e.g. headers for data encryption
            key headers.

    Attributes:
        media_url (str): The URL containing the media to be downloaded.
        start (Optional[int]): The first byte in a range to be downloaded.
        end (Optional[int]): The last byte in a range to be downloaded.
        chunk_size (int): The number of bytes to be retrieved in each request.

    Raises:
        ValueError: If ``start`` is negative.
    """

    def consume_next_chunk(
        self,
        transport,
        timeout=(
            _request_helpers._DEFAULT_CONNECT_TIMEOUT,
            _request_helpers._DEFAULT_READ_TIMEOUT,
        ),
    ):
        """Consume the next chunk of the resource to be downloaded.

        Args:
            transport (~requests.Session): A ``requests`` object which can
                make authenticated requests.
            timeout (Optional[Union[float, Tuple[float, float]]]):
                The number of seconds to wait for the server response.
                Depending on the retry strategy, a request may be repeated
                several times using the same timeout each time.

                Can also be passed as a tuple (connect_timeout, read_timeout).
                See :meth:`requests.Session.request` documentation for details.

        Returns:
            ~requests.Response: The HTTP response returned by ``transport``.

        Raises:
            ValueError: If the current download has finished.
        """
        method, url, payload, headers = self._prepare_request()

        # Wrap the request business logic in a function to be retried.
        def retriable_request():
            # NOTE: We assume "payload is None" but pass it along anyway.
            result = transport.request(
                method,
                url,
                data=payload,
                headers=headers,
                stream=True,
                timeout=timeout,
            )
            self._process_response(result)
            return result

        return _request_helpers.wait_and_retry(
            retriable_request, self._get_status_code, self._retry_strategy
        )


def _add_decoder(response_raw, checksum):
    """Patch the ``_decoder`` on a ``urllib3`` response.

    This is so that we can intercept the compressed bytes before they are
    decoded.

    Only patches if the content encoding is ``gzip``.

    Args:
        response_raw (urllib3.response.HTTPResponse): The raw response for
            an HTTP request.
        checksum (object):
            A checksum which will be updated with compressed bytes.

    Returns:
        object: Either the original ``checksum`` if ``_decoder`` is not
        patched, or a ``_DoNothingHash`` if the decoder is patched, since the
        caller will no longer need to hash to decoded bytes.
    """
    encoding = response_raw.headers.get("content-encoding", "").lower()
    if encoding != "gzip":
        return checksum

    response_raw._decoder = _GzipDecoder(checksum)
    return _helpers._DoNothingHash()


class _GzipDecoder(urllib3.response.GzipDecoder):
    """Custom subclass of ``urllib3`` decoder for ``gzip``-ed bytes.

    Allows a checksum function to see the compressed bytes before they are
    decoded. This way the checksum of the compressed value can be computed.

    Args:
        checksum (object):
            A checksum which will be updated with compressed bytes.
    """

    def __init__(self, checksum):
        super(_GzipDecoder, self).__init__()
        self._checksum = checksum

    def decompress(self, data):
        """Decompress the bytes.

        Args:
            data (bytes): The compressed bytes to be decompressed.

        Returns:
            bytes: The decompressed bytes from ``data``.
        """
        self._checksum.update(data)
        return super(_GzipDecoder, self).decompress(data)
