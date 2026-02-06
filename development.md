# Development documentation

## Releasing

To create a new release:

1. Run the release script with a semantic version bump:
   ```bash
   ./scripts/release.sh patch   # Bug fixes (0.1.0 -> 0.1.1)
   ./scripts/release.sh minor   # New features (0.1.0 -> 0.2.0)
   ./scripts/release.sh major   # Breaking changes (0.1.0 -> 1.0.0)
   ```

2. The script will:
   - Update version in `pyproject.toml` and `src/ticketlog/__init__.py`
   - Create a commit and tag
   - Push to GitHub
   - Create a draft release

3. Review the draft release on GitHub, edit release notes if needed, then publish.

4. Publishing the release triggers the GitHub Actions workflow to publish to PyPI.
