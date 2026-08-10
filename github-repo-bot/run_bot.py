#!/usr/bin/env python3
"""
GitHub Repository Enhancement Bot Runner
Easy-to-use interface for creating professional repositories
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
import subprocess

console = Console()

def main():
    """Main runner interface"""
    
    # Display banner
    console.print(Panel.fit(
        "[bold blue]🚀 GitHub Repository Enhancement Bot[/bold blue]\n"
        "[dim]Transform any repository into a professional, multi-developer codebase[/dim]\n\n"
        "[yellow]⚡ Quick Setup Guide ⚡[/yellow]\n"
        "1. Ensure you have Python 3.8+ installed\n"
        "2. Set your GITHUB_TOKEN environment variable\n"
        "3. Run this script to create amazing repositories!",
        border_style="blue",
        title="🎯 Professional Repository Creator"
    ))
    
    # Check prerequisites
    if not check_prerequisites():
        return
    
    # Get user preferences
    config = get_user_configuration()
    
    # Display configuration summary
    show_configuration_summary(config)
    
    # Confirm and execute
    if Confirm.ask("\n[bold green]Create repository with above configuration?[/bold green]"):
        execute_bot(config)
    else:
        console.print("[yellow]Operation cancelled[/yellow]")

def check_prerequisites():
    """Check if all prerequisites are met"""
    console.print("\n[bold]Checking Prerequisites...[/bold]")
    
    # Check Python version
    if sys.version_info < (3, 8):
        console.print("[red]✗ Python 3.8+ required[/red]")
        return False
    console.print("[green]✓ Python version OK[/green]")
    
    # Check GitHub token
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        console.print("[red]✗ GITHUB_TOKEN environment variable not set[/red]")
        console.print("[dim]Get your token at: https://github.com/settings/tokens[/dim]")
        
        # Offer to set token interactively
        if Confirm.ask("Would you like to enter your GitHub token now?"):
            token = Prompt.ask("Enter your GitHub token", password=True)
            os.environ['GITHUB_TOKEN'] = token
            console.print("[green]✓ GitHub token set[/green]")
        else:
            return False
    else:
        # Mask token for display
        masked_token = f"{token[:8]}...{token[-4:]}"
        console.print(f"[green]✓ GitHub token found ({masked_token})[/green]")
    
    # Check if dependencies are installed
    try:
        import github
        import requests
        import rich
        console.print("[green]✓ Dependencies installed[/green]")
    except ImportError as e:
        console.print(f"[red]✗ Missing dependency: {e.name}[/red]")
        if Confirm.ask("Install dependencies now?"):
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                             check=True, capture_output=True)
                console.print("[green]✓ Dependencies installed successfully[/green]")
            except subprocess.CalledProcessError:
                console.print("[red]✗ Failed to install dependencies[/red]")
                return False
        else:
            return False
    
    return True

def get_user_configuration():
    """Get user configuration interactively"""
    console.print("\n[bold]Project Configuration[/bold]")

    config = {}

    config["project_path"] = Prompt.ask(
        "[cyan]Local project folder path[/cyan]",
        default=str(Path.cwd()),
    )

    config["repo_name"] = Prompt.ask(
        "[cyan]GitHub repository name[/cyan]",
        default=Path(config["project_path"]).name,
    )

    config["private"] = Confirm.ask(
        "[cyan]Create as private repository?[/cyan]",
        default=True,
    )

    config["commits"] = int(Prompt.ask(
        "[cyan]Number of commits to generate[/cyan]",
        default="50",
    ))

    config["days_back"] = int(Prompt.ask(
        "[cyan]Days back for commit history[/cyan]",
        default="90",
    ))

    config["create_issues"] = Confirm.ask(
        "[cyan]Create GitHub issues now? (cannot backdate created_at)[/cyan]",
        default=False,
    )

    config["create_prs"] = Confirm.ask(
        "[cyan]Create pull requests now? (cannot backdate opened_at)[/cyan]",
        default=False,
    )

    return config

def show_configuration_summary(config):
    """Display configuration summary table"""
    table = Table(title="Repository Configuration Summary")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Project Path", config["project_path"])
    table.add_row("Repository Name", config["repo_name"])
    table.add_row("Privacy", "Private" if config["private"] else "Public")
    table.add_row("Commits", str(config["commits"]))
    table.add_row("History Period", f"{config['days_back']} days")
    table.add_row("Create Issues", "Yes" if config["create_issues"] else "No")
    table.add_row("Create PRs", "Yes" if config["create_prs"] else "No")
    
    console.print(table)

def execute_bot(config):
    """Execute the repository enhancement bot"""
    console.print(f"\n[bold green]🚀 Creating repository '{config['repo_name']}'...[/bold green]")
    
    # Build command
    cmd = [
        sys.executable,
        "bot.py",
        "--project-path",
        config["project_path"],
        "--repo-name",
        config["repo_name"],
        "--commits",
        str(config["commits"]),
        "--days-back",
        str(config["days_back"]),
    ]

    if config["private"]:
        cmd.append("--private")
    else:
        cmd.append("--public")

    if config["create_issues"]:
        cmd.append("--create-issues")
    else:
        cmd.append("--no-create-issues")

    if config["create_prs"]:
        cmd.append("--create-prs")
    else:
        cmd.append("--no-create-prs")
    
    # Execute bot
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        console.print(f"\n[bold green]🎉 Repository '{config['repo_name']}' created successfully![/bold green]")
        
        # Show next steps
        console.print(Panel.fit(
            f"[bold]Next Steps:[/bold]\n\n"
            f"1. Visit: [link]https://github.com/[username]/{config['repo_name']}[/link]\n"
            f"2. Clone locally: [dim]git clone [repo_url][/dim]\n"
            f"3. Start developing your amazing project!\n\n"
            f"[dim]The repository now has:{[/dim]\n"
            f"• {config['commits']} professional commits across 3 developers\n"
            f"• Realistic {config['language']} project structure\n"
            f"• Professional documentation\n"
            f"• {'GitHub issues and ' if config['create_issues'] else ''}proper licensing",
            title="🎯 Success!",
            border_style="green"
        ))
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗ Failed to create repository: {e}[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! 👋[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)