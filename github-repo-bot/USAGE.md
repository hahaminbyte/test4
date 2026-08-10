# GitHub Repository Enhancement Bot - Usage Guide

## 🚀 Quick Start (Recommended)

The fastest way to create a professional repository:

### 1. Update Your GitHub Token

Edit `quick_start.py` and replace the token:

```python
GITHUB_TOKEN = "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this"
```

Replace with your actual GitHub token from: https://github.com/settings/tokens

**Required permissions:** `repo`, `delete_repo`, `user`

### 2. Run the Quick Start

```bash
python3 quick_start.py
```

Choose from professional templates:
- 🤖 AI-Powered Dashboard
- 🔐 Secure API Gateway  
- 💰 Blockchain Trading Bot
- 🎯 ML Recommendation Engine

## 📋 Detailed Usage

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x install.sh
./install.sh
```

### Command Line Interface

```bash
# Basic usage
python3 bot.py --repo-name "my-project"

# Full configuration
python3 bot.py \
  --repo-name "enterprise-app" \
  --commits 75 \
  --days-back 120 \
  --private \
  --create-issues \
  --language typescript
```

### Interactive Mode

```bash
python3 run_bot.py
```

This launches an interactive wizard that guides you through:
- Repository naming
- Language selection
- Commit history configuration
- Feature selection

## 🎯 Usage Examples

### Example 1: Professional Web Platform

```python
from bot import GitHubRepoBot

bot = GitHubRepoBot("your_github_token")

# Create repository
clone_url = bot.create_repository("professional-platform", private=True)
bot.setup_local_repo("professional-platform", clone_url)

# Setup project
bot.create_project_structure("typescript")
bot.generate_commits(85, 120)  # 85 commits over 120 days
bot.create_github_issues("professional-platform", 6)
bot.push_changes()
```

### Example 2: Quick API Project

```python
bot = GitHubRepoBot("your_token")
clone_url = bot.create_repository("api-service")
bot.setup_local_repo("api-service", clone_url)
bot.create_project_structure("python")
bot.generate_commits(50, 90)
bot.push_changes()
```

### Example 3: Enterprise Setup

```bash
python3 bot.py \
  --repo-name "enterprise-microservices" \
  --commits 150 \
  --days-back 180 \
  --create-issues \
  --private \
  --language typescript
```

## ⚙️ Configuration Options

### Repository Settings

| Option | Description | Default |
|--------|-------------|---------|
| `--repo-name` | Repository name | Required |
| `--private` | Create private repository | False |
| `--language` | Primary language | python |
| `--commits` | Number of commits | 50 |
| `--days-back` | Days of history | 90 |
| `--create-issues` | Create GitHub issues | False |

### Supported Languages

- **Python**: Django/FastAPI structure
- **JavaScript**: Node.js/Express structure  
- **TypeScript**: Professional TS setup
- **Go**: Standard Go project layout
- **Rust**: Cargo project structure
- **Java**: Maven project structure

### Developer Personas

The bot creates commits from 3 professional developers:

1. **Alex Rivera** - Senior Full Stack Developer
2. **Sarah Chen** - DevOps Engineer & Architecture Lead  
3. **Marcus Vance** - Security Engineer & Code Quality Specialist

## 🔧 Advanced Features

### Custom Configuration

Edit `config.json` to customize:

```json
{
  "developers": [...],
  "commit_templates": {...},
  "components": [...],
  "technologies": [...]
}
```

### Environment Variables

```bash
export GITHUB_TOKEN="your_token"
export DEFAULT_PRIVATE=true
export DEFAULT_COMMITS=75
export DEFAULT_LANGUAGE=python
```

### Docker Usage

```bash
# Build image
docker build -t github-repo-bot .

# Run with token
docker run -e GITHUB_TOKEN="your_token" github-repo-bot \
  --repo-name "docker-project" --commits 60
```

## 📊 Features Created

### Repository Structure
- Professional README with badges
- LICENSE file (MIT)
- Language-appropriate project structure
- Configuration files (.env.example, Dockerfile, etc.)

### Commit History
- 3 realistic developer personas
- Conventional commit messages
- Realistic timing patterns (business hours, weekdays)
- Clustered commits (burst patterns)
- Professional commit types: feat, fix, refactor, docs, test, chore

### GitHub Integration
- Realistic issues with professional descriptions
- Proper labeling system
- Project boards (optional)
- Branch protection (optional)
- Professional repository metadata

### Generated Issues Examples
- "Memory leak detected in authentication middleware"
- "Implement rate limiting for API endpoints"
- "Security audit findings - JWT token validation"
- "Update API documentation for v2 endpoints"

## 🛡️ Security & Best Practices

### Token Security
- Never commit tokens to version control
- Use environment variables
- Rotate tokens regularly
- Limit token permissions to required scopes only

### Repository Management
- All repositories created as private by default
- Professional commit messages following conventional standards
- Realistic development patterns
- Enterprise-grade project structure

## 🐛 Troubleshooting

### Common Issues

**"Authentication failed"**
- Check your GitHub token is valid
- Verify token has required permissions
- Ensure token hasn't expired

**"Repository already exists"**  
- Choose a different repository name
- Delete existing repository first
- Use a more unique name

**"Git command failed"**
- Ensure git is installed and configured
- Check write permissions in current directory
- Verify internet connection

**"Import errors"**
- Run: `pip install -r requirements.txt`
- Check Python version (3.8+ required)
- Install missing dependencies manually

### Debug Mode

```bash
# Enable verbose output
python3 bot.py --repo-name "debug-test" --verbose

# Check installation
python3 -c "from bot import GitHubRepoBot; print('✓ Import successful')"
```

## 🤝 Support

If you encounter issues:

1. Check this troubleshooting guide
2. Verify your GitHub token and permissions
3. Ensure all dependencies are installed
4. Run with `--verbose` flag for detailed output

## 🚨 Important Notes

- **Token Security**: Keep your GitHub token secure and never share it
- **Rate Limits**: GitHub API has rate limits; the bot handles these automatically
- **Repository Cleanup**: Delete test repositories to avoid clutter
- **Professional Use**: This tool creates realistic repositories for legitimate purposes

## 📈 Tips for Best Results

1. **Use descriptive repository names** that match your project domain
2. **Choose appropriate commit counts** (50-100 for new projects, 100+ for mature ones)
3. **Select realistic time periods** (60-120 days for most projects)
4. **Enable issues creation** for more realistic repository activity
5. **Match language to your actual project** for proper GitHub language detection

---

**Happy repository building! 🎉**