#!/usr/bin/env python3
"""
Integrated GitHub Tools Setup
Uses established tools: git-history-editor, fake-it-til-you-git, and PyGithub
Based on the comprehensive prompt requirements
"""

import os
import sys
import json
import random
import subprocess
import tempfile
from datetime import datetime, timedelta
from typing import List, Dict, Any
from github import Github
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class IntegratedGitHubTools:
    """Integration with established GitHub enhancement tools"""
    
    def __init__(self, token: str):
        self.token = token
        self.github = Github(token)
        self.user = self.github.get_user()
        
        # Professional developers as specified in the prompt
        self.developers = [
            {"name": "Alex Rivera", "email": "alex.rivera@codepulse.dev"},
            {"name": "Sarah Chen", "email": "sarah.chen@codepulse.dev"},
            {"name": "Marcus Vance", "email": "marcus.vance@codepulse.dev"}
        ]
        
    def install_required_tools(self):
        """Install and setup required tools"""
        
        console.print("[blue]Setting up required tools...[/blue]")
        
        # Check if git is available
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            console.print("[green]✓ Git is available[/green]")
        except:
            console.print("[red]✗ Git not found. Please install git first.[/red]")
            return False
            
        # Check Node.js for git-history-editor (if using web version)
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
            console.print("[green]✓ Node.js available for web tools[/green]")
        except:
            console.print("[yellow]⚠ Node.js not found (optional for some features)[/yellow]")
        
        return True
    
    def create_repository_with_fake_it_til_you_git(self, repo_name: str):
        """Use fake-it-til-you-git approach for commit generation"""
        
        console.print(f"[blue]Creating repository with fake-it-til-you-git approach: {repo_name}[/blue]")
        
        # Create repository on GitHub first
        try:
            repo = self.user.create_repo(
                name=repo_name,
                description="Professional repository with realistic commit history",
                private=True,
                has_issues=True,
                has_projects=True,
                auto_init=False
            )
            
            clone_url = repo.clone_url.replace("https://", f"https://{self.token}@")
            console.print(f"[green]✓ GitHub repository created: {repo.html_url}[/green]")
            
        except Exception as e:
            console.print(f"[red]✗ Repository creation failed: {e}[/red]")
            return False
            
        # Setup local repository
        if os.path.exists(repo_name):
            subprocess.run(["rm", "-rf", repo_name], check=True)
            
        subprocess.run(["git", "clone", clone_url], check=True)
        os.chdir(repo_name)
        
        # Create professional structure
        self._create_professional_files()
        
        # Use fake-it-til-you-git methodology
        self._generate_fake_history_with_multiple_authors()
        
        # Push to GitHub
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        console.print(f"[green]✓ Repository '{repo_name}' created with realistic history[/green]")
        return True
    
    def _create_professional_files(self):
        """Create professional file structure for language detection"""
        
        # Create LICENSE file (Apache-2.0 as specified)
        license_content = '''Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Copyright 2024 Professional Development Team

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.'''
        
        with open("LICENSE", "w") as f:
            f.write(license_content)
        
        # Create TypeScript files for proper language detection
        os.makedirs("src", exist_ok=True)
        os.makedirs("tests", exist_ok=True)
        
        # Main TypeScript application
        with open("src/index.ts", "w") as f:
            f.write('''/**
 * Professional TypeScript Application
 * Enterprise-grade architecture with advanced features
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { createServer } from 'http';
import { Logger } from './utils/logger';
import { DatabaseManager } from './database/manager';
import { AuthenticationService } from './services/auth';

const logger = new Logger('Application');

class ProfessionalApplication {
  private app: express.Application;
  private server: any;
  private readonly port: number;

  constructor() {
    this.app = express();
    this.port = Number(process.env.PORT) || 3000;
    this.setupMiddleware();
    this.setupRoutes();
  }

  private setupMiddleware(): void {
    // Security middleware
    this.app.use(helmet());
    this.app.use(cors({
      origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000']
    }));
    
    // Request parsing
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true }));
  }

  private setupRoutes(): void {
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
      });
    });

    this.app.get('/api/status', (req, res) => {
      res.json({
        service: 'Professional API',
        version: '1.0.0',
        environment: process.env.NODE_ENV || 'development'
      });
    });
  }

  async start(): Promise<void> {
    try {
      // Initialize database
      await DatabaseManager.initialize();
      
      // Start HTTP server
      this.server = createServer(this.app);
      this.server.listen(this.port, () => {
        logger.info(`Server running on port ${this.port}`);
      });
      
    } catch (error) {
      logger.error('Failed to start application', error);
      process.exit(1);
    }
  }

  async shutdown(): Promise<void> {
    logger.info('Shutting down application...');
    if (this.server) {
      this.server.close();
    }
    await DatabaseManager.close();
  }
}

// Start application
const app = new ProfessionalApplication();
app.start();

// Graceful shutdown
process.on('SIGTERM', () => app.shutdown());
process.on('SIGINT', () => app.shutdown());
''')

        # Supporting TypeScript files
        os.makedirs("src/utils", exist_ok=True)
        with open("src/utils/logger.ts", "w") as f:
            f.write('''export class Logger {
  constructor(private context: string) {}

  info(message: string, meta?: any): void {
    console.log(JSON.stringify({
      level: 'info',
      context: this.context,
      message,
      timestamp: new Date().toISOString(),
      ...(meta && { meta })
    }));
  }

  error(message: string, error?: any): void {
    console.error(JSON.stringify({
      level: 'error', 
      context: this.context,
      message,
      error: error?.message || error,
      timestamp: new Date().toISOString()
    }));
  }
}''')

        # Package.json for TypeScript detection
        package_json = {
            "name": "professional-enterprise-platform",
            "version": "1.0.0",
            "description": "Professional enterprise platform with TypeScript",
            "main": "dist/index.js",
            "scripts": {
                "build": "tsc",
                "start": "node dist/index.js",
                "dev": "ts-node src/index.ts",
                "test": "jest"
            },
            "dependencies": {
                "express": "^4.18.0",
                "cors": "^2.8.5",
                "helmet": "^7.0.0"
            },
            "devDependencies": {
                "typescript": "^5.0.0",
                "@types/node": "^20.0.0",
                "ts-node": "^10.9.0"
            }
        }
        
        with open("package.json", "w") as f:
            json.dump(package_json, f, indent=2)
        
        # Professional README
        with open("README.md", "w") as f:
            f.write('''# Professional Enterprise Platform

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)

Enterprise-grade platform built with professional development practices.

## Features

- 🚀 High-performance TypeScript architecture
- 🔐 Advanced security implementation
- 📊 Comprehensive monitoring and logging
- 🛡️ Enterprise-grade error handling
- ⚡ Optimized for production workloads

## Quick Start

```bash
npm install
npm run build
npm start
```

## License

Apache License 2.0 - see [LICENSE](LICENSE) file.
''')

        console.print("[green]✓ Professional file structure created[/green]")
    
    def _generate_fake_history_with_multiple_authors(self):
        """Generate fake commit history using git commands (fake-it-til-you-git approach)"""
        
        console.print("[blue]Generating realistic commit history...[/blue]")
        
        # Professional commit messages (as specified in prompt)
        commit_messages = [
            "feat: implement secure token exchange",
            "refactor: optimize async worker queues", 
            "fix: handle edge cases in parser",
            "docs: update API specification and integration guides",
            "chore: clean up legacy configuration dependencies",
            "style: format codebase according to enterprise lint rules",
            "test: add unit coverage for core authentication middleware",
            "feat: initialize project architecture and core scaffolding",
            "refactor: optimize asynchronous worker queue performance",
            "fix: handle unhandled exception during high-load state checks",
            "feat: implement advanced user authentication system",
            "refactor: restructure database connection pooling",
            "fix: resolve memory leak in background processing",
            "docs: add comprehensive API documentation",
            "chore: update dependencies to latest stable versions"
        ]
        
        # Initial commit
        subprocess.run(["git", "add", "."], check=True)
        self._create_commit("feat: initialize project architecture and core scaffolding", self.developers[0])
        
        # Generate 12-15 commits with realistic timing
        num_commits = random.randint(12, 15)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Creating commits...", total=num_commits)
            
            for i in range(1, num_commits):
                # Select random developer and message
                dev = random.choice(self.developers)
                msg = random.choice(commit_messages) + f" (ref #{i+1})"
                
                # Make realistic file changes
                self._make_realistic_changes(i)
                
                # Create commit with backdated timestamp
                days_back = random.randint(1, 90)  # Spread over 3 months
                self._create_backdated_commit(msg, dev, days_back)
                
                progress.update(task, advance=1)
        
        console.print("[green]✓ Realistic commit history generated[/green]")
    
    def _make_realistic_changes(self, iteration: int):
        """Make realistic file changes for commits"""
        
        # Modify existing files to create realistic diffs
        if iteration % 3 == 0:
            # Update main application
            with open("src/index.ts", "a") as f:
                f.write(f"\n// Enhancement {iteration}: Improved error handling\n")
        elif iteration % 4 == 0:
            # Update documentation
            with open("README.md", "a") as f:
                f.write(f"\n<!-- Update {iteration}: Documentation improved -->\n")
        else:
            # Update tracking file
            with open(".update_log", "a") as f:
                f.write(f"Update {iteration}: {datetime.now().isoformat()}\n")
        
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
    
    def _create_commit(self, message: str, author: Dict[str, str]):
        """Create commit with specified author"""
        
        env = os.environ.copy()
        env.update({
            "GIT_AUTHOR_NAME": author["name"],
            "GIT_AUTHOR_EMAIL": author["email"],
            "GIT_COMMITTER_NAME": author["name"], 
            "GIT_COMMITTER_EMAIL": author["email"]
        })
        
        subprocess.run(["git", "commit", "-m", message], env=env, check=True)
    
    def _create_backdated_commit(self, message: str, author: Dict[str, str], days_back: int):
        """Create backdated commit (fake-it-til-you-git technique)"""
        
        # Calculate backdated timestamp
        commit_date = datetime.now() - timedelta(days=days_back)
        
        # Adjust to realistic business hours (9 AM to 6 PM)
        hour = random.randint(9, 18)
        minute = random.randint(0, 59)
        commit_date = commit_date.replace(hour=hour, minute=minute)
        
        date_str = commit_date.isoformat()
        
        env = os.environ.copy()
        env.update({
            "GIT_AUTHOR_NAME": author["name"],
            "GIT_AUTHOR_EMAIL": author["email"],
            "GIT_COMMITTER_NAME": author["name"],
            "GIT_COMMITTER_EMAIL": author["email"],
            "GIT_AUTHOR_DATE": date_str,
            "GIT_COMMITTER_DATE": date_str
        })
        
        subprocess.run(["git", "commit", "-m", message], env=env, check=True)
    
    def populate_github_issues(self, repo_name: str):
        """Create realistic GitHub issues using PyGithub"""
        
        console.print("[blue]Populating GitHub issues...[/blue]")
        
        try:
            repo = self.github.get_user().get_repo(repo_name)
            
            # Professional issues as specified in the prompt
            issues_data = [
                (
                    "Memory leak in core worker threads under high load",
                    "Noticed a gradual memory creep during prolonged stress testing. "
                    "Memory usage increases by ~50MB per hour under sustained load of 1000+ concurrent users. "
                    "Needs profiling and investigation of event listener cleanup."
                ),
                (
                    "Add rate limiting to token exchange endpoint", 
                    "To prevent abuse, we should implement sliding window rate limiters on the /auth/token endpoint. "
                    "Requirements: Redis-based storage, configurable limits, proper HTTP 429 responses."
                ),
                (
                    "Refactor configuration loader to support dynamic environment overrides",
                    "Current setup is too rigid for multi-region container deployments. "
                    "Need hierarchical configuration system with environment variables, config files, and runtime overrides."
                )
            ]
            
            for title, body in issues_data:
                repo.create_issue(title=title, body=body)
                
            console.print(f"[green]✓ Created {len(issues_data)} professional GitHub issues[/green]")
            
        except Exception as e:
            console.print(f"[yellow]⚠ Could not create GitHub issues: {e}[/yellow]")
    
    def setup_git_history_editor_integration(self, repo_name: str):
        """Setup for git-history-editor integration"""
        
        console.print("[blue]Setting up git-history-editor integration...[/blue]")
        
        # Create configuration for git-history-editor tool
        config = {
            "repository": repo_name,
            "developers": self.developers,
            "commit_patterns": {
                "feat": 0.3,
                "fix": 0.25, 
                "refactor": 0.2,
                "docs": 0.15,
                "test": 0.1
            },
            "time_distribution": {
                "business_hours": 0.8,
                "evening": 0.15,
                "weekend": 0.05
            }
        }
        
        with open(f"{repo_name}_git_editor_config.json", "w") as f:
            json.dump(config, f, indent=2)
            
        console.print("[green]✓ Git history editor configuration created[/green]")
        console.print("[dim]Use this config with: https://bokub.github.io/git-history-editor[/dim]")


def main():
    """Main function using integrated tools approach"""
    
    console.print(Panel.fit(
        "[bold blue]🛠️ Integrated GitHub Tools Setup[/bold blue]\n"
        "[dim]Using established tools and methodologies[/dim]\n\n"
        "[yellow]Tools Integration:[/yellow]\n"
        "• fake-it-til-you-git methodology\n" 
        "• PyGithub API integration\n"
        "• git-history-editor compatibility\n"
        "• Professional commit patterns",
        border_style="blue"
    ))
    
    # Your GitHub token
    GITHUB_TOKEN = "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this"
    
    try:
        # Initialize integrated tools
        tools = IntegratedGitHubTools(GITHUB_TOKEN)
        
        # Check prerequisites
        if not tools.install_required_tools():
            return
        
        # Repository name
        repo_name = "integrated-professional-platform"
        
        # Create repository using fake-it-til-you-git approach
        success = tools.create_repository_with_fake_it_til_you_git(repo_name)
        
        if success:
            # Populate GitHub issues using PyGithub
            tools.populate_github_issues(repo_name)
            
            # Setup git-history-editor integration
            tools.setup_git_history_editor_integration(repo_name)
            
            console.print(Panel.fit(
                f"[bold green]🎉 Repository Created Successfully![/bold green]\n\n"
                f"[white]Repository:[/white] {repo_name}\n"
                f"[white]URL:[/white] https://github.com/{tools.user.login}/{repo_name}\n"
                f"[white]Tools Used:[/white] fake-it-til-you-git + PyGithub\n"
                f"[white]Developers:[/white] 3 professional personas\n"
                f"[white]License:[/white] Apache-2.0\n\n"
                "[dim]Check the repository for realistic commit history and professional structure![/dim]",
                title="✨ Success!",
                border_style="green"
            ))
        
    except Exception as e:
        console.print(f"[red]✗ Setup failed: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()