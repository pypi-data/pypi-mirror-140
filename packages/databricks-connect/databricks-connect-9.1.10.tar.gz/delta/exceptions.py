#
# Copyright (2021) The Delta Lake Project Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from pyspark import SparkContext
from pyspark.sql import utils
from pyspark.sql.utils import CapturedException


class DeltaConcurrentModificationException(CapturedException):
    """
    The basic class for all Delta commit conflict exceptions.

    .. versionadded:: 1.0

    .. note:: Evolving
    """


class ConcurrentWriteException(CapturedException):
    """
    Thrown when a concurrent transaction has written data after the current transaction read the
    table.

    .. versionadded:: 1.0

    .. note:: Evolving
    """


class MetadataChangedException(CapturedException):
    """
    Thrown when the metadata of the Delta table has changed between the time of read
    and the time of commit.

    .. versionadded:: 1.0

    .. note:: Evolving
    """


class ProtocolChangedException(CapturedException):
    """
    Thrown when the protocol version has changed between the time of read
    and the time of commit.

    .. versionadded:: 1.0

    .. note:: Evolving
    """


class ConcurrentAppendException(CapturedException):
    """
    Thrown when files are added that would have been read by the current transaction.

    .. versionadded:: 1.0

    .. note:: Evolving
    """


class ConcurrentDeleteReadException(CapturedException):
    """
    Thrown when the current transaction reads data that was deleted by a concurrent transaction.

    .. versionadded:: 1.0

    .. note:: Evolving
    """


class ConcurrentDeleteDeleteException(CapturedException):
    """
    Thrown when the current transaction deletes data that was deleted by a concurrent transaction.

    .. versionadded:: 1.0

    .. note:: Evolving
    """


class ConcurrentTransactionException(CapturedException):
    """
    Thrown when concurrent transaction both attempt to update the same idempotent transaction.

    .. versionadded:: 1.0

    .. note:: Evolving
    """


_delta_exception_patched = False
# BEGIN-EDGE
# In DBR, we update pyspark.sql.utils.convert_exception directly, so we don't the patch.
_delta_exception_patched = True
# END-EDGE


# BEGIN-EDGE
# We don't use this method in DBR as we update pyspark.sql.utils.convert_exception directly.
# END-EDGE
def _convert_delta_exception(e):
    """
    Convert Delta's Scala concurrent exceptions to the corresponding Python exceptions.
    """
    s = e.toString()
    c = e.getCause()
    stacktrace = SparkContext._jvm.org.apache.spark.util.Utils.exceptionString(e)

    if s.startswith('io.delta.exceptions.DeltaConcurrentModificationException: '):
        return DeltaConcurrentModificationException(s.split(': ', 1)[1], stacktrace, c)
    if s.startswith('io.delta.exceptions.ConcurrentWriteException: '):
        return ConcurrentWriteException(s.split(': ', 1)[1], stacktrace, c)
    if s.startswith('io.delta.exceptions.MetadataChangedException: '):
        return MetadataChangedException(s.split(': ', 1)[1], stacktrace, c)
    if s.startswith('io.delta.exceptions.ProtocolChangedException: '):
        return ProtocolChangedException(s.split(': ', 1)[1], stacktrace, c)
    if s.startswith('io.delta.exceptions.ConcurrentAppendException: '):
        return ConcurrentAppendException(s.split(': ', 1)[1], stacktrace, c)
    if s.startswith('io.delta.exceptions.ConcurrentDeleteReadException: '):
        return ConcurrentDeleteReadException(s.split(': ', 1)[1], stacktrace, c)
    if s.startswith('io.delta.exceptions.ConcurrentDeleteDeleteException: '):
        return ConcurrentDeleteDeleteException(s.split(': ', 1)[1], stacktrace, c)
    if s.startswith('io.delta.exceptions.ConcurrentTransactionException: '):
        return ConcurrentTransactionException(s.split(': ', 1)[1], stacktrace, c)
    return None


def _patch_convert_exception():
    """
    Patch PySpark's exception convert method to convert Delta's Scala concurrent exceptions to the
    corresponding Python exceptions.
    """
    convert_sql_exception = utils.convert_exception

    def convert_delta_exception(e):
        delta_exception = _convert_delta_exception(e)
        if delta_exception is not None:
            return delta_exception
        return convert_sql_exception(e)

    utils.convert_exception = convert_delta_exception


if not _delta_exception_patched:
    _patch_convert_exception()
    _delta_exception_patched = True
