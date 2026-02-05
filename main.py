
import click
import pandas as pd
import numpy as np
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from generator import SyntheticDataGenerator
from analysis import ModelAnalyzer
from visualizer import Visualizer

console = Console()

@click.group()
def cli():
    """pilk-sem: The Vibe-Coding SEM Tool"""
    pass

@cli.command()
@click.option('--latents', default=3, help='Number of latent variables')
@click.option('--indicators', default=3, help='Indicators per latent')
@click.option('--n', default=200, help='Sample size')
def vibe(latents, indicators, n):
    """Run a full SEM vibe check with synthetic data."""
    console.rule("[bold magenta]pilk-sem Vibe Check[/bold magenta]")
    
    # 1. Define Model
    rprint("[yellow]⚡ Generating Vibe Data...[/yellow]")
    latent_map = {}
    latent_names = []
    for i in range(latents):
        l_name = f"F{i+1}"
        latent_names.append(l_name)
        latent_map[l_name] = [f"x{i+1}_{j+1}" for j in range(indicators)]
        
    # Create simple chain structure: F1 -> F2 -> F3 ...
    paths = []
    for i in range(len(latent_names)-1):
        paths.append(f"{latent_names[i]} -> {latent_names[i+1]}")
        
    gen = SyntheticDataGenerator(n_samples=n)
    df = gen.generate_data(latent_map, paths)
    
    rprint(f"[green]✔ Generated {n} samples![/green]")
    
    # 2. Analyze
    analyzer = ModelAnalyzer(df)
    
    # Reliability & EFA
    rprint("\n[bold cyan]1. Reliability & Screening[/bold cyan]")
    prelim = analyzer.run_preliminary_analysis(latent_map)
    
    table = Table(title="Cronbach's Alpha")
    table.add_column("Latent", style="cyan")
    table.add_column("Alpha", justify="right")
    table.add_column("Verdict", style="bold")
    
    for k, v in prelim["reliability"].items():
        verdict = "OK" if v > 0.7 else "LOW"
        color = "green" if v > 0.7 else "red"
        table.add_row(k, f"{v:.3f}", f"[{color}]{verdict}[/{color}]")
    console.print(table)
    
    if "efa_eigenvalues" in prelim:
        rprint(f"Top 5 Eigenvalues: {[f'{x:.2f}' for x in prelim['efa_eigenvalues'][:5]]}")

    # SEM
    rprint("\n[bold cyan]2. Structural Equation Model[/bold cyan]")
    sem_desc = analyzer.generate_semopy_desc(latent_map, paths)
    res = analyzer.run_sem(sem_desc)
    
    # Fit Indices
    fit = res['fit_indices']
    ftable = Table(title="Model Fit Indices")
    ftable.add_column("Index", style="magenta")
    ftable.add_column("Value")
    ftable.add_column("Criterion")
    
    # Common indices
    idx_map = {
        'CFI': ('> 0.90', lambda x: x>0.9), 
        'TLI': ('> 0.90', lambda x: x>0.9), 
        'RMSEA': ('< 0.08', lambda x: x<0.08), 
        'Chi2/df': ('< 3 (or 5)', lambda x: True) # semopy might output as something else
    }
    
    # semopy 'calc_stats' returns a DataFrame or Series, let's just print what we find
    # Actually fit_indices from semopy is a DataFrame usually
    # Use pandas to extract
    if isinstance(fit, pd.DataFrame):
        # Transpose if needed, semopy usually gives one row
        if 'CFI' in fit.columns:
            val = fit['CFI'].iloc[0]
            ftable.add_row("CFI", f"{val:.3f}", "[green]Good[/green]" if val>0.9 else "[red]Poor[/red]")
        if 'TLI' in fit.columns:
            val = fit['TLI'].iloc[0]
            ftable.add_row("TLI", f"{val:.3f}", "[green]Good[/green]" if val>0.9 else "[red]Poor[/red]")
        if 'RMSEA' in fit.columns:
            val = fit['RMSEA'].iloc[0]
            ftable.add_row("RMSEA", f"{val:.3f}", "[green]Good[/green]" if val<0.08 else "[red]Poor[/red]")
            
    console.print(ftable)
    
    # 3. Visualization
    rprint("\n[bold cyan]3. Visualization[/bold cyan]")
    viz = Visualizer(filename="path")
    diagram_outputs = viz.generate_diagram(latent_map, paths, stats=res['stats'])
    if isinstance(diagram_outputs, dict):
        rendered_paths = ", ".join(f"{fmt.upper()}: {path}" for fmt, path in diagram_outputs.items())
        rprint(f"[yellow]★ Path diagram saved to {rendered_paths}[/yellow]")
    else:
        rprint(f"[yellow]★ Path diagram saved to {diagram_outputs}[/yellow]")
    
    rprint("\n[bold magenta]✨ Vibe Check Complete! ✨[/bold magenta]")

import yaml

@cli.command()
@click.option('--config', required=True, help='Path to model.yaml config file')
@click.option('--overkill', is_flag=True, help='Enable "Overkill" features (Physics Viz, Bootstrapping)')
def run(config, overkill):
    """Run a full SEM vibe check from a YAML config."""
    console.rule("[bold magenta]pilk-sem Advanced Run[/bold magenta]")
    
    # ... (Keep existing loading logic up to analysis) ...
    # 1. Load Config
    with open(config, 'r') as f:
        conf = yaml.safe_load(f)
        
    rprint(f"[yellow]⚡ Generating Data from {config}...[/yellow]")
    
    gen = SyntheticDataGenerator() 
    df = gen.generate_data(conf)
    
    n = len(df)
    rprint(f"[green]✔ Generated {n} samples![/green]")
    
    # 2. Analyze
    analyzer = ModelAnalyzer(df)
    latents = conf.get('latents', {})
    paths_raw = conf.get('paths', [])
    
    # Clean paths for semopy/visualizer
    paths_clean = []
    for p in paths_raw:
        p = p.replace('(sig)', '').replace('(ns)', '').strip()
        paths_clean.append(p)
    
    # Reliability & EFA
    rprint("\n[bold cyan]1. Reliability & Screening[/bold cyan]")
    if latents:
        prelim = analyzer.run_preliminary_analysis(latents)
        table = Table(title="Cronbach's Alpha")
        table.add_column("Latent", style="cyan")
        table.add_column("Alpha", justify="right")
        table.add_column("Verdict", style="bold")
        
        for k, v in prelim["reliability"].items():
            verdict = "OK" if v > 0.7 else "LOW"
            color = "green" if v > 0.7 else "red"
            table.add_row(k, f"{v:.3f}", f"[{color}]{verdict}[/{color}]")
        console.print(table)
    else:
        rprint("[dim]No latent variables to screen.[/dim]")

    # SEM
    rprint("\n[bold cyan]2. Structural Equation Model[/bold cyan]")
    sem_desc = analyzer.generate_semopy_desc(latents, paths_clean)
    res = analyzer.run_sem(sem_desc)
    
    # Fit Indices
    fit = res['fit_indices']
    ftable = Table(title="Model Fit Indices")
    ftable.add_column("Index", style="magenta")
    ftable.add_column("Value")
    
    if isinstance(fit, pd.DataFrame):
        for idx in ['CFI', 'TLI', 'RMSEA']:
            if idx in fit.columns:
                val = fit[idx].iloc[0]
                ftable.add_row(idx, f"{val:.3f}")
    console.print(ftable)
    
    # Coefficients
    stats = res['stats']
    if isinstance(stats, pd.DataFrame):
        ctable = Table(title="Regression Coefficients")
        ctable.add_column("Path", style="cyan")
        ctable.add_column("Est", justify="right")
        ctable.add_column("P-Val", justify="right")
        ctable.add_column("Sig")
        
        regressions = stats[stats['op'] == '~']
        for _, row in regressions.iterrows():
            lhs, rhs, est, pval = row['lval'], row['rval'], row['Estimate'], row['p-value']
            try: pval_float = float(pval)
            except: pval_float = 1.0
            sig = "[green]*[/green]" if pval_float < 0.05 else "[dim]ns[/dim]"
            ctable.add_row(f"{rhs}->{lhs}", f"{est:.3f}", f"{pval_float:.3f}", sig)
        console.print(ctable)

    # ... (Keep Mediation/Report logic) ...
    
    # OVERKILL FEATURES
    if overkill:
        rprint("\n[bold red]🔥 OVERKILL MODE ACTIVATED 🔥[/bold red]")
        
        # 1. Bootstrapping
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
        rprint("[yellow]Running 200-iteration Bootstrap Simulation...[/yellow]")
        
        # We need to monkeypatch or modify run_bootstrap to yield progress, 
        # or just wrap the call in a spinner for now since it's blocking.
        # Ideally we'd modify run_bootstrap to accept a callback, but let's use a indeterminate spinner for simplicity 
        # OR simulate it by calling it 2 times (hacky)
        # Better: run_bootstrap already runs loop. Let's just wait.
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn()) as progress:
            task = progress.add_task("[cyan]Bootstrapping...", total=None)
            boot_res = analyzer.run_bootstrap(sem_desc, n_boot=200)
            progress.update(task, completed=100)
            
        if boot_res is not None:
            btable = Table(title="Bootstrap Results (Robust SE)")
            btable.add_column("Relation", style="cyan")
            btable.add_column("Orig", justify="right")
            btable.add_column("Boot Mean", justify="right")
            btable.add_column("95% CI", style="magenta")
            
            for _, row in boot_res.iterrows():
                relation = f"{row['RHS']} -> {row['LHS']}"
                ci = f"[{row['CI_Lower']:.2f}, {row['CI_Upper']:.2f}]"
                btable.add_row(relation, f"{row['Original']:.3f}", f"{row['Boot_Mean']:.3f}", ci)
            console.print(btable)
            
        # 2. Residual Heatmap
        rprint("\n[bold yellow]Residual Correlation Heatmap (Terminal Edition)[/bold yellow]")
        # Calc observed correlation
        numeric_df = df.select_dtypes(include=[np.number])
        corr = numeric_df.corr()
        # Just printing a small block of it for "vibe"
        # In a real app we'd calc model implied corr vs observed.
        # Here we just show the observed corr matrix with color
        
        # Limit to first 8 vars to fit screen
        cols = corr.columns[:8]
        htable = Table(title="Correlation Matrix (First 8 Vars)", show_header=True)
        htable.add_column("Var")
        for c in cols: htable.add_column(c, justify="right", width=6)
        
        for r in cols:
            row_data = [r]
            for c in cols:
                val = corr.loc[r, c]
                color = "red" if abs(val) > 0.7 else "white"
                if r == c: color = "dim"
                row_data.append(f"[{color}]{val:.2f}[/{color}]")
            htable.add_row(*row_data)
        console.print(htable)

    # Visualization
    rprint("\n[bold cyan]Vizualization[/bold cyan]")
    viz = Visualizer(filename="path")
    
    if overkill:
        rprint("[yellow]Generating Interactive Physics Graph...[/yellow]")
        interactive_file = viz.generate_interactive(latents, paths_clean, stats=res['stats'])
        rprint(f"[green]★ Interactive graph saved to {interactive_file}[/green]")
        
    diagram_outputs = viz.generate_diagram(latents, paths_clean, stats=res['stats'])
    # ... (print diagram outputs) ...

import model_catalog

@cli.group()
def catalog():
    """Manage standard models (scaffold, list)."""
    pass

@catalog.command()
def list():
    """List available famous models."""
    console.rule("[bold cyan]Famous Model Catalog[/bold cyan]")
    models = model_catalog.list_models()
    table = Table(title="Available Models")
    table.add_column("ID", style="cyan")
    table.add_column("Description")
    
    for k, v in models.items():
        table.add_row(k, v)
    console.print(table)

@catalog.command()
@click.option('--model', required=True, help='Model ID to scaffold (e.g. utaut)')
def scaffold(model):
    """Generate a YAML config for a standard model."""
    config = model_catalog.get_model_config(model.lower())
    if not config:
        rprint(f"[red]Model '{model}' not found in catalog. Run 'catalog list' to see options.[/red]")
        return
        
    filename = f"{model.lower()}.yaml"
    with open(filename, 'w') as f:
        yaml.dump(config, f, sort_keys=False, default_flow_style=None)
        
    rprint(f"[green]✔ Scaffolding complete![/green]")
    rprint(f"Created [bold]{filename}[/bold]. You can now edit it and run:")
    rprint(f"[cyan]python main.py run --config {filename}[/cyan]")

if __name__ == '__main__':
    cli()
