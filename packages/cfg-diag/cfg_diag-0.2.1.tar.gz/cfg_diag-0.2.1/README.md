# A common configuration-storage class with a .diag() method

## Description

This module provides four classes that may be used as base classes for
storing program runtime configuration with a `verbose` boolean field.
The classes provide a `.diag(msg)` method that decides whether to
output the provided message based on the value of the object's
`verbose` field.

The `ConfigDiagUnfrozen` and `ConfigDiagUnfrozenStdOut` classes are
normal dataclasses, while the `ConfigDiag` and `ConfigDiagStdOut` ones
are frozen.

The `ConfigDiag` and `ConfigDiagUnfrozen` classes will output any
diagnostic messages to the standard error stream, while
the `ConfigDiagStdOut` and `ConfigDiagUnfrozenStdOut` ones will output
the diagnostic messages to the standard output stream.

## Example

Subclass the frozen `ConfigDiag` class, add a program-specific field:

    @dataclasses.dataclass(frozen=True)
    class Config(cfg_diag.ConfigDiag):
        """Runtime configuration for the fribble program."""
        path: pathlib.Path

Initialize this class from an argument parser object:

    return Config(path=args.path, verbose=args.verbose)

Output a diagnostic message if requested:

    cfg.diag("This will either appear or it will not")

## Contact

This module is [developed in a GitHub repository][github].
Contact [the StorPool support team][support] for information.

[github]: https://github.com/storpool/python-cfg_diag
[support]: mailto:support@storpool.com
