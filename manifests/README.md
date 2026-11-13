# Repository manifests

These SHA-256 manifests were generated from the repository snapshot before the Jupyter cleanup commit.

- `MANIFEST.sha256` records the repository files in that snapshot.
- `ZIP_CONTENTS.sha256` records files inside the ZIP archives in that snapshot.

The manifest paths are repository-root-relative. Verify them from the repository root with:

```sh
sha256sum --check manifests/MANIFEST.sha256
```

The first manifest is a historical snapshot and therefore includes the Jupyter artifacts removed by the cleanup commit. Regenerate it after any later repository changes if you need a manifest of the current tree.
