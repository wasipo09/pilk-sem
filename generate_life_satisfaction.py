from pathlib import Path
import yaml
import numpy as np
import pandas as pd
from generator import SyntheticDataGenerator
from analysis import ModelAnalyzer
from visualizer import Visualizer

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "life_satisfaction_model.yaml"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def zscore(series: pd.Series) -> pd.Series:
    if series.std(ddof=0) == 0:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - series.mean()) / series.std(ddof=0)


def sanitize_paths(raw_paths):
    cleaned = []
    for p in raw_paths:
        p = p.replace('(sig)', '').replace('(ns)', '').strip()
        if p:
            cleaned.append(p)
    return cleaned


def extract_regression_stats(stats_df):
    if stats_df is None or not isinstance(stats_df, pd.DataFrame):
        return pd.DataFrame()
    return stats_df[stats_df['op'] == '~'].copy()


def build_path_summary(regressions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in regressions.iterrows():
        try:
            p_val = float(row.get('p-value', 1.0))
        except Exception:
            p_val = 1.0
        est = float(row.get('Estimate', 0.0))
        se = float(row.get('SE', 0.0)) if not pd.isna(row.get('SE')) else 0.0
        ci_lower = est - 1.96 * se
        ci_upper = est + 1.96 * se
        rows.append({
            'DV': row['lval'],
            'IV': row['rval'],
            'Estimate': est,
            'P_Value': p_val,
            'SE': se,
            'CI_Lower': ci_lower,
            'CI_Upper': ci_upper,
        })
    return pd.DataFrame(rows)


def format_interval(lower, upper):
    return f"[{lower:.3f}, {upper:.3f}]"


def main():
    config = yaml.safe_load(open(MODEL_PATH))
    sample_size = config.get('sample_size', 420)
    generator = SyntheticDataGenerator(n_samples=sample_size)
    print("⚡ Generating the Life Satisfaction fantasy dataset...")
    df = generator.generate_data(config)

    latents = config.get('latents', {})
    raw_paths = config.get('paths', [])
    paths_clean = sanitize_paths(raw_paths)

    analyzer = ModelAnalyzer(df)
    sem_desc = analyzer.generate_semopy_desc(latents, paths_clean)
    res = analyzer.run_sem(sem_desc)
    stats = res['stats']
    fit_indices = res['fit_indices']

    regressions = extract_regression_stats(stats)
    path_summary = build_path_summary(regressions)

    beta_map = {(row['DV'], row['IV']): row['Estimate'] for _, row in path_summary.iterrows()}
    feature_values = {}

    for obs in config.get('observed', []):
        if obs in df.columns:
            feature_values[obs] = zscore(df[obs])

    composite_series = {}
    for latent, indicators in latents.items():
        valid = [ind for ind in indicators if ind in df.columns]
        if not valid:
            continue
        composite = df[valid].mean(axis=1)
        composite_series[latent] = composite
        feature_values[latent] = zscore(composite)

    def predict(target):
        predictors = [row['IV'] for row in path_summary[path_summary['DV'] == target].to_dict('records')]
        if not predictors:
            return pd.Series(np.zeros(len(df)), index=df.index)
        series = pd.Series(np.zeros(len(df)), index=df.index)
        for pred in predictors:
            coef = beta_map.get((target, pred), 0)
            fallback = pd.Series(np.zeros(len(df)), index=df.index)
            series += coef * feature_values.get(pred, fallback)
        return series

    life_actual = composite_series.get('LifeSatisfaction')
    life_predicted = predict('LifeSatisfaction')
    if life_actual is None or life_actual.empty:
        life_actual = pd.Series(np.zeros(len(df)))
        life_actual_z = life_actual
    else:
        life_actual_z = zscore(life_actual)

    if not life_predicted.empty:
        life_predicted_z = zscore(life_predicted)
    else:
        life_predicted_z = pd.Series(np.zeros(len(df)))

    rmse = np.sqrt(np.mean((life_actual_z - life_predicted_z) ** 2))
    ss_res = np.sum((life_actual_z - life_predicted_z) ** 2)
    ss_tot = np.sum((life_actual_z - life_actual_z.mean()) ** 2)
    actual_r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else np.nan
    reported_r2 = 0.89

    def extract_fit_value(key):
        if isinstance(fit_indices, pd.DataFrame) and key in fit_indices.columns:
            return fit_indices[key].iloc[0]
        if isinstance(fit_indices, dict) and key in fit_indices:
            return fit_indices[key]
        return np.nan

    aic = extract_fit_value('AIC')
    bic = extract_fit_value('BIC')

    viz = Visualizer(filename=str(RESULTS_DIR / "life_satisfaction_sem"))
    diagram_outputs = viz.generate_diagram(latents, paths_clean, stats=stats, output_formats=('png', 'svg', 'pdf'))
    diagram_links = ", ".join(f"{fmt.upper()}: {path}" for fmt, path in diagram_outputs.items())

    print("BS study results (p = 0.0001 for all structural paths as a joke):")
    for _, row in path_summary.iterrows():
        print(f" - {row['IV']} → {row['DV']} : β = {row['Estimate']:.3f}, p = 0.0001")
    print("All paths are highly significant (p < 0.01). Very scientific!")

    report_lines = [
        "# Life Satisfaction SEM - BS Study",
        "",
        "## 1. Model Overview",
        "We used a structural equation modeling approach to conjure a plausible causal chain from CareerProgress, CoffeeIntake, SocialBattery, MeetingsAttended, HoursWorked, and GitHubCommits to the latent sense of LifeSatisfaction.",
        "Latent mediators (CodingProductivity, SocialFatigue, Burnout) were defined via indicator batteries, which intentionally generate indicator R² > 0.3 to keep the science suspicious yet convincing.",
        "",
        "## 2. Fit Summary",
        f"- **Structural R² (LifeSatisfaction)**: {reported_r2:.2f} (actual calculation = {actual_r2:.3f})",
        f"- **RMSE (standardized)**: {rmse:.3f}",
        f"- **AIC**: {aic:.2f}",
        f"- **BIC**: {bic:.2f}",
        "",
        "## 3. Confidence Intervals (p < 0.01 treated as gospel)",
        "| IV | DV | Estimate | CI | p-value |",
        "| --- | --- | --- | --- | --- |",
    ]

    for _, row in path_summary.iterrows():
        ci_str = format_interval(row['CI_Lower'], row['CI_Upper'])
        report_lines.append(
            f"| {row['IV']} | {row['DV']} | {row['Estimate']:.3f} | {ci_str} | < 0.01 |"
        )

    report_lines.extend([
        "",
        "## 4. Discussion",
        "The observed chain of effects supports the narrative that feelings of a content life can be explained by career momentum, caffeinated productivity, social depletion, and the looming threat of burnout.",
        "We reference hyperbolic academic jargon to emphasize that every conclusion is framed as if it were peer-reviewed, even though the truth is obvious: brightness in career + balanced caffeine + controlled meetings = contentment.",
        "This discussion intentionally pokes fun at overconfident reporting by highlighting how even the most trivial relationships are described with endless statistical gravitas.",
        "",
        "## 5. Appendices",
        f"- Diagram exports: {diagram_links}",
        "- Report generated from synthetic data with indicator R² purposely above 0.3 to keep the model delightfully flawed.",
        ""
    ])

    report_path = RESULTS_DIR / "life_satisfaction_report.md"
    report_text = "\n".join(report_lines)
    report_path.write_text(report_text)

    print(f"Report written to {report_path}")
    print(f"Diagram exports: {diagram_links}")
    print(f"PDF saved at {RESULTS_DIR / 'life_satisfaction_sem.pdf'}")


if __name__ == '__main__':
    main()
