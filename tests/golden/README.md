# Golden exposition files

These files hold the exact output of `collect_pve()` for the recorded API
responses in `tests/fixtures/`. They are compared byte for byte, so any diff
in a pull request is either a bug or a deliberate behaviour change that needs
to be explained in the commit message and the changelog.

Regenerate them with:

    pytest --snapshot-update

## Known-wrong behaviour recorded here

These lines were captured from the code as it was when the tests were added.
They are wrong, and the commits that fix them are expected to change them:

- `standalone.txt`, `standalone-cluster-only.txt`:
  `pve_not_backed_up_total{id="cluster/pve0"}`. `pve0` is a standalone node,
  not a cluster. `BackupInfoCollector` reads the name of the first
  `/cluster/status` entry without checking its type.
