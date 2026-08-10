#!/usr/bin/env python3
"""
Quick Start - GitHub Repository Enhancement Bot
Simplified interface for immediate use with your GitHub token
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from bot import GitHubRepoBot

console = Console()

# Your GitHub token - replace with your actual token
GITHUB_TOKEN = "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this"

def create_awesome_repository():
    """Create an awesome repository with one command"""
    
    console.print(Panel.fit(
        "[bold green]🚀 One-Click Professional Repository Creator[/bold green]\n"
        "[dim]Using your GitHub token to create amazing repositories![/dim]",
        border_style="green"
    ))
    
    # Repository configurations - choose one or modify
    repos = [
        {
            "name": "ai-powered-dashboard",
            "language": "typescript",
            "commits": 75,
            "days": 90,
            "description": "AI-powered analytics dashboard with real-time data visualization"
        },
        {
            "name": "secure-api-gateway",
            "language": "python", 
            "commits": 60,
            "days": 75,
            "description": "Enterprise-grade API gateway with advanced security features"
        },
        {
            "name": "blockchain-trading-bot",
            "language": "javascript",
            "commits": 90,
            "days": 120,
            "description": "Automated cryptocurrency trading bot with risk management"
        },
        {
            "name": "ml-recommendation-engine",
            "language": "python",
            "commits": 85,
            "days": 105,
            "description": "Machine learning recommendation engine for e-commerce platforms"
        }
    ]
    
    # Display options
    console.print("[bold]Select a repository to create:[/bold]")
    for i, repo in enumerate(repos, 1):
        console.print(f"{i}. [cyan]{repo['name']}[/cyan] ({repo['language']}) - {repo['description']}")
    
    choice = input("\nEnter choice (1-4) or press Enter for option 1: ").strip()
    
    if not choice:
        choice = "1"
    
    try:
        selected_repo = repos[int(choice) - 1]
    except (ValueError, IndexError):
        console.print("[red]Invalid choice, using default...[/red]")
        selected_repo = repos[0]
    
    console.print(f"\n[green]Creating: {selected_repo['name']}[/green]")
    
    try:
        # Initialize bot
        bot = GitHubRepoBot(GITHUB_TOKEN)
        
        # Create repository with progress tracking
        steps = [
            "Creating GitHub repository...",
            "Setting up local environment...", 
            "Building project structure...",
            "Generating commit history...",
            "Creating GitHub issues...",
            "Pushing to GitHub..."
        ]
        
        for step in track(steps, description="Building repository..."):
            if "Creating GitHub" in step:
                clone_url = bot.create_repository(
                    repo_name=selected_repo["name"],
                    private=True,
                    description=selected_repo["description"]
                )
            elif "Setting up local" in step:
                bot.setup_local_repo(selected_repo["name"], clone_url)
            elif "Building project" in step:
                bot.create_project_structure(selected_repo["language"])
            elif "Generating commit" in step:
                bot.generate_commits(selected_repo["commits"], selected_repo["days"])
            elif "Creating GitHub issues" in step:
                bot.create_github_issues(selected_repo["name"], num_issues=5)
            elif "Pushing to GitHub" in step:
                bot.push_changes()
        
        # Success message
        console.print(Panel.fit(
            f"[bold green]🎉 Repository Created Successfully![/bold green]\n\n"
            f"[white]Repository:[/white] {selected_repo['name']}\n"
            f"[white]Language:[/white] {selected_repo['language'].title()}\n"
            f"[white]Commits:[/white] {selected_repo['commits']} professional commits\n"
            f"[white]History:[/white] {selected_repo['days']} days of development\n\n"
            f"[dim]Visit your repository on GitHub to see the amazing commit history![/dim]",
            title="✨ Success!",
            border_style="green"
        ))
        
        # Display repository summary
        bot.display_summary(selected_repo["name"])
        
    except Exception as e:
        console.print(f"[red]Error creating repository: {e}[/red]")
        console.print("[yellow]Make sure your GitHub token is valid and has proper permissions.[/yellow]")
        sys.exit(1)

def quick_custom_repo():
    """Quick custom repository creator"""
    
    console.print("[bold]Quick Custom Repository Creator[/bold]")
    
    # Get user input
    repo_name = input("Repository name: ").strip() or "my-awesome-project"
    
    languages = ["python", "javascript", "typescript", "go", "rust"]
    print("\nLanguages:", ", ".join(f"{i+1}.{lang}" for i, lang in enumerate(languages)))
    lang_choice = input("Language (1-5, default 1): ").strip()
    
    try:
        language = languages[int(lang_choice) - 1] if lang_choice else languages[0]
    except (ValueError, IndexError):
        language = "python"
    
    commits = int(input("Number of commits (default 50): ").strip() or "50")
    days = int(input("Days of history (default 90): ").strip() or "90")
    
    console.print(f"\n[green]Creating custom repository: {repo_name}[/green]")
    
    try:
        bot = GitHubRepoBot(GITHUB_TOKEN)
        
        clone_url = bot.create_repository(repo_name, private=True)
        bot.setup_local_repo(repo_name, clone_url)
        bot.create_project_structure(language)
        bot.generate_commits(commits, days)
        bot.create_github_issues(repo_name)
        bot.push_changes()
        
        console.print(f"[bold green]Custom repository '{repo_name}' created successfully![/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def main():
    """Main interface"""
    
    console.print(Panel.fit(
        "[bold blue]GitHub Repository Enhancement Bot[/bold blue]\n"
        "[dim]Professional repository creation made simple[/dim]",
        border_style="blue"
    ))
    
    # Verify token
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your_token_here":
        console.print("[red]Please update GITHUB_TOKEN in this script with your actual token![/red]")
        console.print("[dim]Get your token at: https://github.com/settings/tokens[/dim]")
        sys.exit(1)
    
    console.print("[bold]Choose an option:[/bold]")
    console.print("1. Create from templates (recommended)")
    console.print("2. Custom repository")
    console.print("3. Exit")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == "1":
        create_awesome_repository()
    elif choice == "2":
        quick_custom_repo()
    elif choice == "3":
        console.print("[yellow]Goodbye![/yellow]")
    else:
        console.print("[red]Invalid choice[/red]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")