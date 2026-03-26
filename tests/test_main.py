"""Tests for main module."""

from python_project import __version__


def test_version():
    """Test that version is defined and correct."""
    assert __version__ == "0.1.0"


def test_main(capsys):
    """Test main function prints expected output."""
    from python_project import main

    main()
    captured = capsys.readouterr()
    assert "Hello from Python Project!" in captured.out
