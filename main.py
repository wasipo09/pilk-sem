
import click
import pandas as pd
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
    out_file = viz.generate_diagram(latent_map, paths, stats=res['stats'])
    rprint(f"[yellow]★ Path diagram saved to {out_file}[/yellow]")
    
    rprint("\n[bold magenta]✨ Vibe Check Complete! ✨[/bold magenta]")

import yaml

@cli.command()
@click.option('--config', required=True, help='Path to model.yaml config file')
def run(config):
    """Run a full SEM vibe check from a YAML config."""
    console.rule("[bold magenta]pilk-sem Advanced Run[/bold magenta]")
    
    # 1. Load Config
    with open(config, 'r') as f:
        conf = yaml.safe_load(f)
        
    rprint(f"[yellow]⚡ Generating Data from {config}...[/yellow]")
    
    gen = SyntheticDataGenerator() # Sample size is in config now
    df = gen.generate_data(conf)
    
    n = len(df)
    rprint(f"[green]✔ Generated {n} samples![/green]")
    
    # 2. Analyze
    analyzer = ModelAnalyzer(df)
    latents = conf.get('latents', {})
    paths_raw = conf.get('paths', [])
    
    # Clean paths for semopy/visualizer (remove (sig)/(ns))
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
        
        if "efa_eigenvalues" in prelim:
            rprint(f"Top 5 Eigenvalues: {[f'{x:.2f}' for x in prelim['efa_eigenvalues'][:5]]}")
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
    ftable.add_column("Criterion")
    
    if isinstance(fit, pd.DataFrame):
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
    
    # Coefficients (to prove sig/ns)
    stats = res['stats']
    if isinstance(stats, pd.DataFrame):
        ctable = Table(title="Regression Coefficients")
        ctable.add_column("Path", style="cyan")
        ctable.add_column("Estimate", justify="right")
        ctable.add_column("P-Value", justify="right")
        ctable.add_column("Sig", style="bold")
        
        # Filter for Regressions (~)
        regressions = stats[stats['op'] == '~']
        for _, row in regressions.iterrows():
            lhs, rhs, est, pval = row['lval'], row['rval'], row['Estimate'], row['p-value']
            try:
                pval_float = float(pval)
            except ValueError:
                pval_float = 1.0 # Treat as non-sig if error
            
            is_sig = pval_float < 0.05
            sig_str = "[green]*[/green]" if is_sig else "[dim]ns[/dim]"
            p_str = "< 0.001" if pval_float < 0.001 else f"{pval_float:.3f}"
            
            ctable.add_row(f"{rhs} -> {lhs}", f"{est:.3f}", p_str, sig_str)
        
        console.print(ctable)
    # 2.5 Mediation Analysis
    rprint("\n[bold cyan]3. Mediation Analysis[/bold cyan]")
    med_results = analyzer.calculate_mediation(res['stats'])
    if med_results:
        mtable = Table(title="Indirect Effects")
        mtable.add_column("Mediator Chain", style="magenta")
        mtable.add_column("Effect", justify="right")
        mtable.add_column("P-Value", justify="right")
        mtable.add_column("Sig", style="bold")
        
        for m in med_results:
            chain = f"{m['IV']} -> {m['Mediator']} -> {m['DV']}"
            p_val = m['P_Value']
            is_sig = p_val < 0.05
            sig_str = "[green]*[/green]" if is_sig else "[dim]ns[/dim]"
            p_str = "< 0.001" if p_val < 0.001 else f"{p_val:.3f}"
            
            mtable.add_row(chain, f"{m['Indirect_Effect']:.3f}", p_str, sig_str)
        console.print(mtable)
    else:
        rprint("[dim]No significant indirect paths detected.[/dim]")

    # 2.6 Auto-Report
    rprint("\n[bold cyan]4. Auto-Report Generation[/bold cyan]")
    report = analyzer.generate_academic_report(
        res['stats'], 
        res['fit_indices'], 
        prelim['reliability'] if latents else {}, 
        med_results
    )
    with open("results_report.md", "w") as f:
        f.write(report)
    rprint("[green]📝 Academic report written to 'results_report.md'[/green]")

    # 3. Visualization
    rprint("\n[bold cyan]5. Visualization[/bold cyan]")

    viz = Visualizer(filename="path")
    out_file = viz.generate_diagram(latents, paths_clean, stats=res['stats'])
    rprint(f"[yellow]★ Path diagram saved to {out_file}[/yellow]")
    
    rprint("\n[bold magenta]✨ Vibe Check Complete! ✨[/bold magenta]")

if __name__ == '__main__':
    cli()
