# README Standards

A comprehensive guide to writing effective README documentation for software projects. This document serves as the knowledge base for the readme pattern.

## Table of Contents

1. [Core Principles](#core-principles)
2. [Essential Sections](#essential-sections)
3. [Writing Guidelines](#writing-guidelines)
4. [Section Templates](#section-templates)
5. [Project Type Variations](#project-type-variations)
6. [Quality Checklist](#quality-checklist)

---

## Core Principles

### The Three Questions

A great README answers three fundamental questions in the first few paragraphs:

| Question | Answer In |
|----------|-----------|
| What is this? | Title and first paragraph |
| Why should I care? | Overview/description |
| How do I use it? | Quick Start section |

### Progressive Disclosure

Structure information from general to specific:

| Time | User Should |
|------|-------------|
| 10 seconds | Understand what it is |
| 30 seconds | Know if it's relevant |
| 5 minutes | Get started using it |
| When needed | Find detailed documentation |

### Key Principles

| Principle | Description |
|-----------|-------------|
| Clarity | Use simple, direct language |
| Completeness | Include all essential sections |
| Accuracy | Keep information current |
| Scannability | Use headings, lists, and code blocks |

---

## Essential Sections

### Required Sections (In Order)

1. **Project Title** - Clear, descriptive name
2. **One-line Description** - What it does and who it's for
3. **Overview** - 2-3 sentences expanding on the description
4. **Installation** - Prerequisites and step-by-step instructions
5. **Quick Start** - Working example users can run immediately
6. **Usage** - Detailed usage examples
7. **License** - License information

### Recommended Sections

| Section | When to Include |
|---------|-----------------|
| Badges | Public/open source projects |
| Table of Contents | READMEs longer than 200 lines |
| Features | Projects with multiple capabilities |
| Configuration | Projects with config options |
| API Reference | Libraries with programmatic APIs |
| Examples | Complex projects |
| Contributing | Open source projects |
| Testing | Projects with test suites |
| Acknowledgments | Projects with contributors/dependencies |

---

## Writing Guidelines

### Language and Style

**DO:**

- Use simple, direct language in active voice
- Write short sentences and paragraphs
- Define technical terms on first use
- Provide context for decisions

**DON'T:**

- Use vague language ("the usual setup")
- Include placeholder text ("TODO", "Coming soon")
- Create walls of text
- Assume reader knowledge without explanation

### Code Examples

**Good code examples:**

```bash
# Install the package
npm install my-package

# Run the example
npm run example
```

**Bad code examples:**

```bash
# TODO: Add installation command
install-command-here
```

### Formatting

| Element | Use For |
|---------|---------|
| `# Title` | Main title (use once) |
| `## Section` | Major sections |
| `### Subsection` | Subsections |
| `**bold**` | Emphasis and key terms |
| `` `code` `` | Variables, commands, file names |
| `> quote` | Important notes and warnings |
| Tables | Structured data |

### Visual Hierarchy

- Place key metrics and KPIs prominently
- Group related information together
- Use consistent panel sizes for related content
- Create visual separation between sections
- Use rows/sections to organize

---

## Section Templates

### Installation Section

```markdown
## Installation

### Prerequisites

- Node.js 18 or higher
- npm 9 or higher
- Git 2.30+

### Quick Install

\`\`\`bash
npm install my-package
\`\`\`

### From Source

\`\`\`bash
git clone https://github.com/user/project.git
cd project
npm install
npm run build
\`\`\`

### Verification

\`\`\`bash
my-package --version
# Expected output: my-package v1.0.0
\`\`\`
```

### Quick Start Section

```markdown
## Quick Start

Create your first project in under 60 seconds:

\`\`\`bash
# Initialize a new project
my-package init my-project
cd my-project

# Run the development server
my-package serve
\`\`\`

Open http://localhost:3000 to see your project.
For detailed usage, see the [Usage](#usage) section.
```

### Configuration Section

```markdown
## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `API_KEY` | API authentication key | Yes | - |
| `DEBUG` | Enable debug logging | No | `false` |
| `PORT` | Server port | No | `3000` |

### Configuration File

Create a `config.yaml` file:

\`\`\`yaml
server:
  port: 3000
  host: localhost

logging:
  level: info
  format: json
\`\`\`
```

### Contributing Section

```markdown
## Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `npm test`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Setup

\`\`\`bash
git clone https://github.com/user/project.git
cd project
npm install
npm run dev
\`\`\`
```

---

## Project Type Variations

### CLI Tool

**Emphasize:**

- Command-line usage examples
- Available commands and options
- Input/output formats
- Shell completion setup

**Example sections:**

```markdown
## Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize a new project |
| `build` | Build the project |
| `serve` | Start development server |

## Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Enable verbose output |
| `-c, --config` | Specify config file |
```

### Library/Package

**Emphasize:**

- API documentation
- Code examples for common use cases
- Type definitions
- Integration examples

**Example sections:**

```markdown
## API Reference

### `myFunction(options)`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `options.name` | `string` | Yes | Name of the resource |
| `options.timeout` | `number` | No | Timeout in ms (default: 5000) |

**Returns:** `Promise<Result>`
```

### Web Application

**Emphasize:**

- Live demo link
- Screenshots/GIFs
- Deployment instructions
- Browser support

**Example sections:**

```markdown
## Demo

Try the live demo at https://example.com/demo

## Screenshots

![Dashboard](./docs/screenshots/dashboard.png)
*Dashboard view showing key metrics*
```

### Framework/SDK

**Emphasize:**

- Architecture overview
- Getting started guide
- Plugin/extension system
- Migration guides

### Monorepo

**Emphasize:**

- Package structure
- Workspace commands
- Cross-package dependencies
- Individual package READMEs

---

## Quality Checklist

### Before Publishing

- [ ] Answers "what, why, how" in first paragraphs
- [ ] Installation instructions are complete with versions
- [ ] At least one working example in Quick Start
- [ ] All code blocks specify language
- [ ] Prerequisites include version numbers
- [ ] No placeholder text (TODO, Coming soon)
- [ ] No walls of text - uses lists, code blocks, headings
- [ ] Verification steps after installation
- [ ] License section present
- [ ] Links work correctly

### For Open Source

- [ ] Contributing guidelines
- [ ] Code of conduct (or link to one)
- [ ] Issue templates mentioned
- [ ] Badges for build status, version, license
- [ ] Acknowledgments for contributors

### For Enterprise

- [ ] Security considerations
- [ ] Support contact information
- [ ] SLA information (if applicable)
- [ ] Compliance/certification info

---

## Badges and Visual Elements

### Shields.io Badges

Badges provide at-a-glance project status. Place after title, limit to 5-8.

**Recommended badges:**

```markdown
![Build Status](https://img.shields.io/github/actions/workflow/status/username/repo/ci.yml?branch=main)
![Coverage](https://img.shields.io/codecov/c/github/username/repo)
![Version](https://img.shields.io/github/v/release/username/repo)
![License](https://img.shields.io/github/license/username/repo)
![Go Version](https://img.shields.io/github/go-mod/go-version/username/repo)
```

**Badge categories:**

| Category | Purpose |
|----------|---------|
| Build status | CI/CD pipeline status |
| Coverage | Code coverage percentage |
| Version | Latest release |
| License | Project license type |
| Downloads | Package download count |
| Social | Stars, forks, contributors |

### Screenshots and GIFs

Visual elements improve comprehension dramatically.

**When to use:**

- CLI tools → Show terminal output
- Web apps → Include screenshots
- Libraries → Show code examples with results
- Performance tools → Display graphs and metrics

**Best practices:**

- Keep images under 500KB
- GIFs max 30 seconds
- Provide alt text for accessibility
- Store in `docs/images/` directory
- Use relative paths

**Tools:**

| Tool | Purpose |
|------|---------|
| [Terminalizer](https://github.com/faressoft/terminalizer) | Record terminal sessions |
| [asciinema](https://asciinema.org/) | Terminal recorder |
| [Carbon](https://carbon.now.sh/) | Code screenshots |
| [Mermaid](https://mermaid.js.org/) | Diagrams in markdown |
| [Excalidraw](https://excalidraw.com/) | Architecture diagrams |

---

## Advanced Sections

### Architecture Section

For complex projects:

```markdown
## Architecture

### High-Level Overview

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Gateway   │────▶│   Service   │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  Database   │
                                        └─────────────┘

### Components

- **Gateway** - Routes requests, handles authentication
- **Service** - Business logic and data processing
- **Database** - PostgreSQL for persistent storage

See [docs/architecture.md](docs/architecture.md) for details.
```

### Troubleshooting Section

```markdown
## Troubleshooting

### Connection timeout error

**Symptoms:** Requests fail with timeout after 30 seconds

**Solution:**
1. Check network: `ping api.example.com`
2. Verify firewall allows outbound HTTPS
3. Increase timeout: `export TIMEOUT=60`

### Getting Help

- Check [existing issues](https://github.com/user/repo/issues)
- Ask in [Discussions](https://github.com/user/repo/discussions)
- Join our [Discord](https://discord.gg/example)
```

### Performance Section

```markdown
## Performance

### Benchmarks

Tested on MacBook Pro M1, 16GB RAM:

| Operation | Time | Memory | Records/sec |
|-----------|------|--------|-------------|
| Parse | 1.2s | 120MB | 833,333 |
| Transform | 0.8s | 80MB | 1,250,000 |

### Optimization Tips

- Use streaming for files over 100MB
- Enable caching with `--cache` flag
- Process in parallel with `--workers=4`
```

### Security Section

```markdown
## Security

### Reporting Vulnerabilities

Report security issues to security@example.com. Do not open public issues.

### Security Features

- All communication uses TLS 1.3
- Passwords hashed with bcrypt (cost factor 12)
- API keys encrypted at rest using AES-256

### Best Practices

1. Never commit API keys or credentials
2. Use environment variables for secrets
3. Regularly rotate API keys
```

### Deployment Section

```markdown
## Deployment

### Docker

\`\`\`bash
docker pull username/project:latest
docker run -p 3000:3000 -e API_KEY=$API_KEY username/project:latest
\`\`\`

### Kubernetes

\`\`\`bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
\`\`\`

### Cloud Platforms

- **AWS:** [Deploy to ECS](docs/deploy-aws.md)
- **GCP:** [Deploy to Cloud Run](docs/deploy-gcp.md)
- **Azure:** [Deploy to Container Instances](docs/deploy-azure.md)
```

---

## Tools and Resources

### README Templates

| Resource | Description |
|----------|-------------|
| [Best-README-Template](https://github.com/othneildrew/Best-README-Template) | Comprehensive template |
| [Standard Readme](https://github.com/RichardLitt/standard-readme) | Standardized specification |
| [Readme.so](https://readme.so/) | Visual README editor |
| [Make a README](https://www.makeareadme.com/) | Simple guide and template |

### Linters and Validators

| Tool | Purpose |
|------|---------|
| [markdownlint](https://github.com/DavidAnson/markdownlint) | Markdown linting |
| [markdown-link-check](https://github.com/tcort/markdown-link-check) | Check for broken links |
| [alex](https://github.com/get-alex/alex) | Check for insensitive writing |
| [write-good](https://github.com/btford/write-good) | Writing style checker |

### GitHub Action for README Validation

```yaml
name: README Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check links
        uses: gaurav-nelson/github-action-markdown-link-check@v1
      - name: Lint markdown
        uses: DavidAnson/markdownlint-cli2-action@v14
```

---

## Real-World Examples

### Outstanding READMEs

Study these for inspiration:

| Project | Notable Feature |
|---------|-----------------|
| [esbuild](https://github.com/evanw/esbuild) | Performance graphs and benchmarks |
| [Astro](https://github.com/withastro/astro) | Perfect balance of features and getting started |
| [Supabase](https://github.com/supabase/supabase) | Great visual hierarchy |
| [FastAPI](https://github.com/tiangolo/fastapi) | Excellent documentation |
| [Rich](https://github.com/Textualize/rich) | Visual demonstrations |

### What Makes Them Great

- Answer "what, why, how" immediately
- Include working examples
- Clear visual hierarchy
- Show rather than tell
- Maintained and up-to-date

---

## Maintenance

### Keep It Current

A README is never "done." Maintain it as you would code.

**With each release:**

- [ ] Update version numbers
- [ ] Update screenshots if UI changed
- [ ] Add new features to features list
- [ ] Test all code examples
- [ ] Check all links

**Quarterly:**

- [ ] Review and update prerequisites
- [ ] Refresh benchmark data
- [ ] Check for broken links
- [ ] Update contributor list

### Version Your Documentation

```markdown
## Documentation Versions

- [Latest (main)](README.md)
- [v2.0](https://github.com/user/project/blob/v2.0/README.md)
- [v1.0](https://github.com/user/project/blob/v1.0/README.md)
```

### Get Feedback

- Monitor issues for documentation requests
- Watch for repeated questions (gaps in docs)
- Survey users periodically

---

## Common Mistakes

### Too Vague

**Bad:**

```markdown
Install the tool using the standard method.
Configure it as needed for your environment.
```

**Good:**

```markdown
Install with npm:
\`\`\`bash
npm install -g mytool
\`\`\`

Configure by creating `~/.mytool.yaml`:
\`\`\`yaml
api_key: your-api-key
region: us-west-2
\`\`\`
```

### Missing Prerequisites

**Bad:**

```markdown
## Installation
Run `make install` to install.
```

**Good:**

```markdown
## Installation

### Prerequisites
- Go 1.21 or higher
- Make 4.0+
- PostgreSQL 14+ (for database features)

### Install
\`\`\`bash
make install
\`\`\`
```

### No Working Examples

**Bad:**

```markdown
## Usage
Use the API to do things.
```

**Good:**

```markdown
## Usage

\`\`\`python
from mylib import Client

client = Client(api_key="your-key")
result = client.process("Hello, World!")
print(result)
# Output: "HELLO, WORLD!"
\`\`\`
```

---

## References

- [Make a README](https://www.makeareadme.com/)
- [Awesome README](https://github.com/matiassingers/awesome-readme)
- [Standard Readme](https://github.com/RichardLitt/standard-readme)
- [Art of README](https://github.com/hackergrrl/art-of-readme)

---

*Last updated: 2026-01-10*
