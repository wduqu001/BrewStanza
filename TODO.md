# BrewStanza MVP TODO

## Week 1 — Foundation

### 1.1 Project Setup
- [ ] Create GitHub repository `brewstanza` with README
- [ ] Initialize Python project (`pyproject.toml`)
- [ ] Setup directory structure (`src/`, `tests/`, `docs/`)
- [ ] Install dependencies (click, rich, toml, pytest, pytest-cov)
- [ ] Setup virtual environment + `requirements.txt`
- [ ] Add `.gitignore`
- [ ] Configure pytest in `pyproject.toml`

### 1.2 CLI Foundation
- [ ] Create CLI entry (`src/brewstanza/cli.py`)
- [ ] Implement main command group (`brewstanza`)
- [ ] Add `brew` subcommand
- [ ] Add `apps` subcommand
- [ ] Add `--version` and `--help`
- [ ] Configure console script entry point

### 1.3 Homebrew Scanner
- [ ] Create scanner module
- [ ] Implement `run_brew_command()`
- [ ] Implement `list_formulae()`
- [ ] Implement `list_casks()`
- [ ] Implement `get_package_info()`
- [ ] Implement `get_outdated_packages()`
- [ ] Implement `calculate_package_size()`

### 1.4 UI Renderer
- [ ] Create UI module
- [ ] Setup Rich renderer
- [ ] Implement package table rendering
- [ ] Implement package detail view

### Week 1 Deliverables
- [ ] CLI works (`--help`, `--version`)
- [ ] List formulae and casks
- [ ] Show package info
- [ ] Output formatted with Rich


---

## Week 2 — Core Features

### 2.1 Application Scanner
- [ ] Create apps scanner module
- [ ] Implement directory scanning
- [ ] Scan `/Applications`
- [ ] Scan `~/Applications`
- [ ] Parse `Info.plist`
- [ ] Calculate app size
- [ ] Implement `get_app_info()`
- [ ] Deduplicate apps

### 2.2 Storage Analyzer
- [ ] Create analyzer module
- [ ] Calculate Homebrew storage
- [ ] Calculate app storage
- [ ] Storage by category
- [ ] Top consumers
- [ ] Size formatter

### 2.3 Categorization
- [ ] Create categorizer module
- [ ] Define category mappings
- [ ] Detect browser apps (PWAs, Chrome apps)
- [ ] Implement `categorize_app()`

### 2.4 UI Enhancements
- [ ] Render app table with categories
- [ ] Render storage breakdown
- [ ] Render removal instructions
- [ ] Add theme support (dark/light)

### Week 2 Deliverables
- [ ] List applications
- [ ] Group by category
- [ ] Show app details
- [ ] Storage breakdown works
- [ ] Accurate size calculations


---

## Week 3 — Integration

### 3.1 Export Manager
- [ ] Create exporter module
- [ ] Implement JSON export
- [ ] Implement Markdown export
- [ ] Implement Brewfile export
- [ ] Add export CLI command

### 3.2 GitHub Integration
- [ ] Create GitHub integration module
- [ ] Add PyGithub dependency
- [ ] Load GitHub config
- [ ] Sync exports to repo
- [ ] Add sync CLI command

### 3.3 Testing
- [ ] Unit tests (scanner)
- [ ] Integration tests (CLI)
- [ ] Coverage reporting
- [ ] Manual macOS testing

### 3.4 Documentation & Release
- [ ] Write README with usage
- [ ] Add screenshots / demos
- [ ] Add LICENSE (MIT)
- [ ] Add CONTRIBUTING.md
- [ ] Add CHANGELOG.md
- [ ] Create Homebrew formula
- [ ] Publish v1.0.0 release

### Week 3 Deliverables
- [ ] JSON export works
- [ ] Markdown export works
- [ ] Brewfile export works
- [ ] GitHub sync works
- [ ] >80% test coverage
- [ ] Public repo + release
- [ ] Homebrew install available


---

## Summary
- Total Tasks: 47
- Estimated Effort: 60-75 hours
- Timeline: 3 weeks