import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.markdown import Markdown

from core.system_scanner import SystemScanner
from core.log_parser import LogParser
from core.triage_engine import TriageEngine
from core.ai_resolver import AIResolver

console = Console(force_terminal=True)


def print_banner():
    banner = r"""
========================================================================
   ___         _          ___            _      _    ___ 
  / _ \  __ _ | |_  ___  |   \  ___  ___ | |__  /_\  |_ _|
 / /_\ \/ _` ||  _|/ _ \ | |) |/ -_)(_-< | / / / _ \  | | 
/_/   \_\\__,_| \__|\___/ |___/ \___|/__/ |_\_\/_/ \_\|___|
                                                            
      AUTODESK AI: AUTOMATED IT SUPPORT & SRE AGENT        
      Author: Syed Saqeeb Ali (AIML Undergraduate)         
========================================================================
    """
    console.print(banner, style="bold cyan")


def display_system_vitals():
    console.print("\n[bold yellow]🩺 Scanning Live System Vitals & Network Health...[/bold yellow]")
    scanner = SystemScanner()
    data = scanner.scan_full_system()

    # Hardware Vitals Table
    vitals = data["vitals"]
    v_table = Table(title="System Hardware & Resource Status", border_style="blue")
    v_table.add_column("Resource", style="bold white")
    v_table.add_column("Current Metric", style="cyan")
    v_table.add_column("Status / Warning", style="magenta")

    v_table.add_row("CPU Load", f"{vitals['cpu']['percent']}% ({vitals['cpu']['cores']} Cores)", "Spike Alert" if vitals['cpu']['percent'] > 80 else "Normal")
    v_table.add_row("RAM Memory", f"{vitals['memory']['used_gb']} GB / {vitals['memory']['total_gb']} GB ({vitals['memory']['percent']}%)", "Heavy Load" if vitals['memory']['percent'] > 85 else "Optimal")
    v_table.add_row("Disk Space", f"{vitals['disk']['free_gb']} GB Free ({vitals['disk']['percent']}% Full)", "Warning" if vitals['disk']['percent'] > 90 else "Adequate")
    
    net = data["network"]
    net_status = f"{net['latency_ms']} ms" if net['online'] else "OFFLINE"
    v_table.add_row("Network / DNS Ping", net_status, net['status'])

    console.print(v_table)

    # Top Resource Consuming Processes
    p_table = Table(title="Top Memory-Consuming Processes", border_style="green")
    p_table.add_column("PID", style="yellow")
    p_table.add_column("Process Name", style="bold white")
    p_table.add_column("Memory %", style="cyan")
    p_table.add_column("CPU %", style="magenta")

    for p in data["top_processes"]:
        p_table.add_row(str(p['pid']), p['name'], f"{p['memory_percent']}%", f"{p['cpu_percent']}%")

    console.print(p_table)


def run_incident_diagnosis(log_content: str):
    console.print("\n[bold cyan]🔍 Parsing Log Tokens & Signatures...[/bold cyan]")
    parsed = LogParser.parse_log_text(log_content)

    scanner = SystemScanner()
    vitals = scanner.get_hardware_vitals()
    triage = TriageEngine.evaluate_priority(parsed, vitals)

    # Display Triage Badge
    p_color = triage["color"]
    console.print(Panel(
        f"[bold {p_color}]SEVERITY TIER: {triage['priority']} - {triage['severity_name']}[/bold {p_color}]\n"
        f"[white]Assigned Team: [bold cyan]{triage['assigned_team']}[/bold cyan][/white]\n"
        f"[white]Target SLA: [bold yellow]{triage['sla_display']}[/bold yellow][/white]\n"
        f"[dim]{triage['description']}[/dim]",
        title="[bold]Automated Incident Triage[/bold]",
        border_style=p_color
    ))

    console.print(f"[bold white]Detected Primary Error:[/bold white] [bold red]{parsed['primary_error']}[/bold red]")
    if parsed['categories']:
        console.print(f"[dim]Signatures: {', '.join(parsed['categories'])}[/dim]\n")

    # Run AI Resolver
    console.print("[bold yellow]🤖 Running Deep Root-Cause Engine...[/bold yellow]")
    resolver = AIResolver()
    diagnosis = resolver.diagnose_issue(log_content, parsed, triage, vitals)

    # Print Root Cause
    console.print(Panel(
        f"[bold green]Root Cause Assessment:[/bold green]\n{diagnosis['root_cause']}\n\n"
        f"[dim]Engine Source: {diagnosis['ai_source']}[/dim]",
        title="[bold]Diagnostic Finding[/bold]",
        border_style="green"
    ))

    # Print Remediation Steps
    console.print("\n[bold cyan]📋 Immediate Remediation Checklist:[/bold cyan]")
    for i, step in enumerate(diagnosis['remediation_steps'], 1):
        console.print(f"  [bold yellow]{i}.[/bold yellow] {step}")

    # Print Fix Commands
    console.print("\n[bold magenta]⚡ Automated Fix / Investigation Commands:[/bold magenta]")
    syntax = Syntax(diagnosis['fix_commands'], "powershell" if os.name == "nt" else "bash", theme="monokai", line_numbers=True)
    console.print(syntax)

    # Prevention
    if diagnosis.get("prevention"):
        console.print("\n[bold blue]🛡️ Long-Term Prevention Advice:[/bold blue]")
        for prev in diagnosis['prevention']:
            console.print(f"  • {prev}")


def handle_log_file_selection():
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_logs")
    sample_files = [f for f in os.listdir(sample_dir) if f.endswith(".log")] if os.path.exists(sample_dir) else []

    console.print("\n[bold cyan]Select a sample log or enter a custom file path:[/bold cyan]")
    for i, f in enumerate(sample_files, 1):
        console.print(f"  [yellow]{i}[/yellow]. sample_logs/{f}")
    console.print(f"  [yellow]{len(sample_files)+1}[/yellow]. Enter custom file path")

    choice = Prompt.ask("\nEnter choice number", default="1")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(sample_files):
            file_path = os.path.join(sample_dir, sample_files[idx])
        else:
            file_path = Prompt.ask("Enter full path to log file")
    except ValueError:
        file_path = Prompt.ask("Enter full path to log file")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        run_incident_diagnosis(content)
    else:
        console.print(f"[bold red]Error: File not found at '{file_path}'[/bold red]")


def handle_manual_error_input():
    console.print("\n[bold cyan]Paste your error message or stack trace below (press Enter twice to submit):[/bold cyan]")
    lines = []
    while True:
        try:
            line = input()
            if not line and lines and not lines[-1]:
                break
            lines.append(line)
        except EOFError:
            break
    
    text = "\n".join(lines).strip()
    if text:
        run_incident_diagnosis(text)
    else:
        console.print("[yellow]No content provided.[/yellow]")


def main():
    print_banner()
    while True:
        console.print("\n" + "─" * 65, style="dim")
        console.print("[bold white]Main Menu:[/bold white]")
        console.print("  [bold cyan]1.[/bold cyan] 🩺 Run Live System & Network Health Scan")
        console.print("  [bold cyan]2.[/bold cyan] 🔍 Triage & Diagnose a Log File")
        console.print("  [bold cyan]3.[/bold cyan] ✍️ Paste an Error Traceback for Instant Fix")
        console.print("  [bold cyan]4.[/bold cyan] 🌐 Launch Web Dashboard (Streamlit)")
        console.print("  [bold cyan]5.[/bold cyan] 🚪 Exit")
        
        choice = Prompt.ask("\nSelect an action", choices=["1", "2", "3", "4", "5"], default="1")

        if choice == "1":
            display_system_vitals()
        elif choice == "2":
            handle_log_file_selection()
        elif choice == "3":
            handle_manual_error_input()
        elif choice == "4":
            console.print("\n[bold green]Launching Streamlit Web Dashboard...[/bold green]")
            os.system("streamlit run app.py")
        elif choice == "5":
            console.print("\n[bold cyan]Exiting AutoDesk AI. Have a productive day![/bold cyan]")
            sys.exit(0)


if __name__ == "__main__":
    main()
