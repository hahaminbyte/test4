#!/usr/bin/env python3
"""
Example Usage - GitHub Repository Enhancement Bot
Demonstrates how to use the bot with your GitHub token
"""

import os
import sys
from bot import GitHubRepoBot
from rich.console import Console
from rich.panel import Panel

console = Console()

def example_create_professional_repo():
    """Example: Create a professional repository with all features"""
    
    # Your GitHub token (replace with your actual token)
    GITHUB_TOKEN = "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this"
    
    console.print(Panel.fit(
        "[bold blue]GitHub Repository Enhancement Bot - Example[/bold blue]\n"
        "[dim]Creating a professional repository with realistic history[/dim]",
        border_style="blue"
    ))
    
    try:
        # Initialize the bot
        bot = GitHubRepoBot(GITHUB_TOKEN)
        
        # Configuration
        repo_name = "professional-web-platform"
        
        console.print(f"[green]Creating repository: {repo_name}[/green]")
        
        # Step 1: Create the repository
        clone_url = bot.create_repository(
            repo_name=repo_name,
            private=True,  # Set to False for public repository
            description="Professional web platform with advanced authentication and real-time features"
        )
        
        # Step 2: Setup local repository
        bot.setup_local_repo(repo_name, clone_url)
        
        # Step 3: Create professional project structure
        bot.create_project_structure(language="typescript")  # or "python", "javascript"
        
        # Step 4: Generate realistic commit history
        bot.generate_commits(
            num_commits=85,    # Number of commits to create
            days_back=120      # Spread commits over 120 days
        )
        
        # Step 5: Create professional GitHub issues
        bot.create_github_issues(repo_name, num_issues=6)
        
        # Step 6: Push all changes to GitHub
        bot.push_changes()
        
        # Step 7: Display summary
        bot.display_summary(repo_name)
        
        console.print(f"\n[bold green]🎉 Success! Repository created: https://github.com/[username]/{repo_name}[/bold green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

def example_quick_setup():
    """Example: Quick repository setup with minimal configuration"""
    
    GITHUB_TOKEN = "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this"
    
    bot = GitHubRepoBot(GITHUB_TOKEN)
    
    # Quick setup
    repo_name = "quick-api-project"
    clone_url = bot.create_repository(repo_name, private=True)
    bot.setup_local_repo(repo_name, clone_url)
    bot.create_project_structure("python")
    bot.generate_commits(30, 60)  # 30 commits over 60 days
    bot.push_changes()
    
    console.print(f"[green]Quick setup complete: {repo_name}[/green]")

def example_enterprise_setup():
    """Example: Enterprise-grade repository with all professional features"""
    
    GITHUB_TOKEN = "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this"
    
    console.print("[bold]Creating Enterprise Repository...[/bold]")
    
    bot = GitHubRepoBot(GITHUB_TOKEN)
    
    # Enterprise configuration
    repo_name = "enterprise-microservices-platform"
    clone_url = bot.create_repository(
        repo_name=repo_name,
        private=True,
        description="Enterprise-grade microservices platform with advanced security, monitoring, and scalability features"
    )
    
    bot.setup_local_repo(repo_name, clone_url)
    bot.create_project_structure("typescript")
    
    # Generate extensive history (looks very professional)
    bot.generate_commits(
        num_commits=150,   # Extensive commit history
        days_back=180      # 6 months of history
    )
    
    # Create comprehensive issues
    bot.create_github_issues(repo_name, num_issues=12)
    
    bot.push_changes()
    bot.display_summary(repo_name)
    
    console.print("[green]Enterprise repository setup complete![/green]")

if __name__ == "__main__":
    # Choose which example to run
    console.print("[bold]GitHub Repository Bot Examples[/bold]")
    console.print("1. Professional Web Platform")
    console.print("2. Quick API Project") 
    console.print("3. Enterprise Microservices Platform")
    
    choice = input("\nSelect example (1-3): ")
    
    if choice == "1":
        example_create_professional_repo()
    elif choice == "2":
        example_quick_setup()
    elif choice == "3":
        example_enterprise_setup()
    else:
        console.print("[red]Invalid choice[/red]")
        
    console.print("\n[dim]Remember to keep your GitHub token secure![/dim]")