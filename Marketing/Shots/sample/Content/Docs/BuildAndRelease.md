# Build and Release

Builds run on every merge to `main`. A release is a tag.

## Making a test build

1. Merge to `main`.
2. Wait for the build to finish.
3. Download the archive from the build page.

## Making a release

Tag the commit `vX.Y.Z` and write the notes. The build uploads itself.

## When a build fails

Read the first error, not the last. Most failures are a missing include or an asset saved by a newer editor.
