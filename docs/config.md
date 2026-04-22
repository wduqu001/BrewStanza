# Configuration Schema

BrewStanza uses a configuration file located at `~/.config/brewstanza/config.toml`.

## Schema

The configuration file is divided into sections.

### `[github]`

Settings related to GitHub synchronization.

- `token` (string): Your GitHub Personal Access Token (PAT). Requires `repo` permissions if pushing to private repositories.
- `repository` (string): The GitHub repository to sync with, in `owner/repo` format (e.g., `wduqu001/dotfiles`).
- `branch` (string): The branch to commit and push to. Default: `"main"`.

### `[scanner]`

Settings related to the disk scanning behaviour.

- `concurrency` (integer): The number of concurrent disk scanning operations to perform. Default: `8`.
- `timeout` (integer): The maximum number of seconds to wait for a single directory scan before timing out. Default: `30`.

## Example `config.toml`

```toml
[github]
token = "ghp_xxxxxxxxxxxxxxxxxxxx"
repository = "wduqu001/dotfiles"
branch = "main"

[scanner]
concurrency = 8
timeout = 30
```
