# Golden exposition files

These files hold the exact output of `collect_pve()` for the recorded API
responses in `tests/fixtures/`. They are compared byte for byte, so any diff
in a pull request is either a bug or a deliberate behaviour change that needs
to be explained in the commit message and the changelog.

Regenerate them with:

    pytest --snapshot-update
