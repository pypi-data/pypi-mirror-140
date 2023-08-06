#
# Copyright (c) 2021  Peter Pentchev <roam@ringlet.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
"""Test the ConfigDiag classes."""

import dataclasses
import sys
import unittest

from unittest import mock

from typing import Any, IO, Optional, Type, Union  # noqa: H301

import ddt  # type: ignore
import pytest

import cfg_diag


TEST_CLASSES = (
    cfg_diag.ConfigDiag,
    cfg_diag.ConfigDiagStdOut,
    cfg_diag.ConfigDiagUnfrozen,
    cfg_diag.ConfigDiagUnfrozenStdOut,
)

ConfigType = Union[Type[cfg_diag.ConfigDiag], Type[cfg_diag.ConfigDiagUnfrozen]]


@ddt.ddt
class TestConfigDiag(unittest.TestCase):
    """Run tests on the ConfigDiag classes."""

    # pylint: disable=no-self-use

    @ddt.data(*TEST_CLASSES)
    def test_frozen(self, cls: ConfigType) -> None:
        """Test some aspect of the ConfigDiag classes."""
        obj = cls(verbose=False)
        assert not obj.verbose

        if "Unfrozen" in cls.__name__:
            obj.verbose = True  # type: ignore
            assert obj.verbose
        else:
            with pytest.raises(dataclasses.FrozenInstanceError):
                obj.verbose = True  # type: ignore
            assert not obj.verbose

    @ddt.data(*TEST_CLASSES)
    def test_no_output(self, cls: ConfigType) -> None:
        """Make sure there is no output with verbose=False."""
        res = []

        def mock_print(msg: str, file: Optional[IO[Any]] = None) -> None:
            """Mock the print() builtin function."""
            res.append((msg, file))

        obj = cls(verbose=False)
        assert not obj.verbose

        with mock.patch("builtins.print", new=mock_print):
            obj.diag("This is not a diagnostic message.")

        assert not res

    @ddt.data(*TEST_CLASSES)
    def test_output(self, cls: ConfigType) -> None:
        """Make sure something is output with verbose=True."""
        to_stdout = "StdOut" in cls.__name__
        res = []

        def mock_print(msg: str, file: Optional[IO[Any]] = None) -> None:
            """Mock the print() builtin function."""
            res.append((msg, file))

        obj = cls(verbose=True)
        assert obj.verbose

        with mock.patch("builtins.print", new=mock_print):
            obj.diag("This is a diagnostic message.")

        assert res == [
            (
                "This is a diagnostic message.",
                sys.stdout if to_stdout else sys.stderr,
            )
        ]
