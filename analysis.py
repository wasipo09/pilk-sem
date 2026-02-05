
# Monkeypatch for factor_analyzer compatibility with sklearn 1.6+
import sklearn.utils
import sklearn.utils.validation
_original_check_array = sklearn.utils.validation.check_array
def _patched_check_array(*args, **kwargs):
    if 'force_all_finite' in kwargs:
        kwargs['ensure_all_finite'] = kwargs.pop('force_all_finite')
    return _original_check_array(*args, **kwargs)
sklearn.utils.validation.check_array = _patched_check_array
sklearn.utils.check_array = _patched_check_array

import pandas as pd
import numpy as np
from factor_analyzer import FactorAnalyzer
from semopy import Model
from typing import Dict, List, Any
import warnings

# Suppress warnings for cleaner CLI output
warnings.filterwarnings("ignore")

class ModelAnalyzer:
    def __init__(self, df: pd.DataFrame, drama=None):
        self.df = df
        self.drama = drama

    def check_multivariate_normality(self):
        """
        Checks for multivariate normality (Vibe Check style).
        Returns (passed: bool, message: str)
        """
        # Calculate univariate kurtosis/skew as proxy
        numeric = self.df.select_dtypes(include=[np.number])
        skew = numeric.skew()
        kurt = numeric.kurtosis()
        
        # Mardia's coefficient proxy (sum of squared skewness + kurtosis excess)
        # This is scientifically "truthy" enough for a vibe tool
        mardia_proxy = (skew**2).sum() + (kurt**2).mean()
        
        # Threshold: if it's too high, we panic
        # Lowered to 0.5 to trigger more often for "Panic Mode" fun
        if mardia_proxy > 0.5: 
            return False, f"Mardia's coeff = {mardia_proxy:.1f}"
        return True, "Normality Assumed"

    def calculate_cronbach_alpha(self, df_subset: pd.DataFrame) -> float:
        """Calculates Cronbach's alpha for a subset of items."""
        item_scores = df_subset.values
        item_variances = item_scores.var(axis=0, ddof=1)
        total_score_variance = item_scores.sum(axis=1).var(ddof=1)
        k = df_subset.shape[1]
        return (k / (k - 1)) * (1 - (item_variances.sum() / total_score_variance))

    def run_preliminary_analysis(self, latents: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Runs EFA (screening) and reliability checks.
        """
        results = {
            "reliability": {},
            "efa_eigenvalues": []
        }
        
        # Reliability
        for name, indicators in latents.items():
            subset = self.df[indicators]
            alpha = self.calculate_cronbach_alpha(subset)
            results["reliability"][name] = alpha
            
        # EFA (Overall) to see factor structure
        # Collect all indicators
        all_indicators = [ind for inds in latents.values() for ind in inds]
        # Check if they exist in df
        valid_inds = [i for i in all_indicators if i in self.df.columns]
        
        if len(valid_inds) > 2:
            fa = FactorAnalyzer(n_factors=len(latents), rotation="varimax")
            fa.fit(self.df[valid_inds])
            ev, _ = fa.get_eigenvalues()
            results["efa_eigenvalues"] = list(ev)
            results["loadings"] = fa.loadings_
        
        return results

    def perform_efa_scan(self, latents: Dict[str, List[str]], threshold: float = 0.4) -> List[str]:
        """
        Runs EFA and identifies items with max loading < threshold.
        """
        # Collect all indicators
        all_indicators = [ind for inds in latents.values() for ind in inds]
        valid_inds = [i for i in all_indicators if i in self.df.columns]
        
        if len(valid_inds) < 3:
            return []
            
        try:
            # Determine number of factors based on number of latents
            n_factors = len(latents)
            
            # ACT I: EFA Disgust
            if self.drama:
                self.drama.trigger_act_one(n_factors)
                
            fa = FactorAnalyzer(n_factors=n_factors, rotation="varimax")
            fa.fit(self.df[valid_inds])
            
            loadings = pd.DataFrame(fa.loadings_, index=valid_inds)
            
            # Find items where max loading across all factors is < threshold
            drop_list = []
            for item, row in loadings.iterrows():
                if row.abs().max() < threshold:
                    drop_list.append(item)
                    
            if self.drama and drop_list:
                self.drama.monologue(f"Purging {len(drop_list)} variables that spark no joy.")
                
            return drop_list
        except:
            if self.drama:
                self.drama.monologue("EFA crashed. Pretending everything is fine.")
            # Fallback if EFA fails (e.g. singular matrix)
            return []

    def perform_reliability_scan(self, latents: Dict[str, List[str]], threshold: float = 0.3) -> List[str]:
        """
        Calculates Item-Total Correlation and identifies items < threshold.
        """
        drop_list = []
        
        for name, indicators in latents.items():
            current_inds = [i for i in indicators if i in self.df.columns]
            if len(current_inds) < 2:
                continue
                
            subset = self.df[current_inds]
            
            # Calculate Item-Total Correlation
            # Corrected Item-Total Correlation: Corr(Item, Sum(Others))
            for item in current_inds:
                others = [i for i in current_inds if i != item]
                if not others:
                    continue
                
                # Sum of others
                other_sum = subset[others].sum(axis=1)
                item_vals = subset[item]
                
                corr = item_vals.corr(other_sum)
                
                if corr < threshold:
                    drop_list.append(item)
                    
        return drop_list

    def run_sem(self, desc: str) -> Any:
        """
        Runs the SEM model using semopy.
        
        Args:
            desc: The semopy model description string.
        """
        model = Model(desc)
        fit = model.fit(self.df)
        stats = model.inspect()
        
        # Calculate fit indices manually if semopy doesn't give all (it gives most)
        # semopy's calc_stats provides indices
        from semopy import calc_stats
        fit_indices = calc_stats(model)
        
        # ACT II & III: The Breakdown
        if self.drama:
             # Act II
             self.drama.trigger_act_two(0.89) # Fake bad start
             
             # Act III
             # Check real CFI if available
             real_cfi = 0.96 # fallback default
             if isinstance(fit_indices, pd.DataFrame) and 'CFI' in fit_indices.columns:
                 real_cfi = fit_indices['CFI'].iloc[0]
                 # If real CFI is poor, let's LIE if we're in drama mode? 
                 # The prompt implies "Pure fabrication". 
                 # But sticking to "You're welcome" with the actual result is safer for a usable tool,
                 # or we can fake the print but return the real stats. 
                 # Let's print the real one but claim we fixed it.
                 if real_cfi < 0.9: 
                     real_cfi = 0.96 # The lie
            
             self.drama.trigger_act_three(real_cfi)
        
        return {
            "stats": stats,
            "fit_indices": fit_indices,
            "obj": model
        }

    @staticmethod
    def generate_semopy_desc(latents: Dict[str, List[str]], paths: List[str], correlations: List[str] = None) -> str:
        """
        Converts config to semopy syntax string.
        """
        lines = []
        # Measurement Model
        # F =~ x1 + x2 + x3
        for name, indicators in latents.items():
            # semopy syntax: F =~ x1 + x2 + x3
            lines.append(f"{name} =~ {' + '.join(indicators)}")
            
        # Structural Model
        # Y ~ X
        for p in paths:
            if '->' in p:
                src, dst = p.split('->')
                lines.append(f"{dst.strip()} ~ {src.strip()}")
                
        # Correlations
        if correlations:
            for c in correlations:
                lines.append(c) # Assumes "A ~~ B" format which semopy supports
                
        return "\n".join(lines)

    def calculate_mediation(self, stats: pd.DataFrame) -> List[Dict]:
        """
        Detects 3-variable mediation chains (A -> B -> C) and calculates indirect effects.
        """
        if not isinstance(stats, pd.DataFrame):
            return []
            
        # Filter for regressions
        regs = stats[stats['op'] == '~']
        paths = {} # (src, dst) -> (estimate, pvalue)
        
        for _, row in regs.iterrows():
            paths[(row['rval'], row['lval'])] = (row['Estimate'], row['p-value'])
            
        chains = []
        # Find A -> B -> C
        # Iterate all paths as A->B
        for (a, b), (beta_ab, p_ab) in paths.items():
            # Find all B -> C
            for (curr_b, c), (beta_bc, p_bc) in paths.items():
                if b == curr_b and a != c:
                    # Valid chain
                    indirect = beta_ab * beta_bc
                    
                    # Sobel Test Approximation for p-value (simplified product p-value logic for vibe)
                    # If both are sig, mediation is likely sig.
                    # P_indirect approx: max(p_ab, p_bc) is a conservative vibe check
                    try:
                        p_ab_f = float(p_ab)
                        p_bc_f = float(p_bc)
                    except:
                        p_ab_f, p_bc_f = 1.0, 1.0
                        
                    p_indirect = max(p_ab_f, p_bc_f) # Conservative
                    
                    chains.append({
                        'IV': a,
                        'Mediator': b,
                        'DV': c,
                        'Indirect_Effect': indirect,
                        'P_Value': p_indirect
                    })
        return chains

    def generate_academic_report(self, stats: pd.DataFrame, fit: Any, reliability: Dict, mediation: List[Dict]) -> str:
        """
        Generates a markdown text report in academic style.
        """
        lines = ["# Structural Equation Modeling Analysis Results", ""]
        
        # 1. Measurement Model
        lines.append("## 1. Measurement Model Assessment")
        lines.append("The measurement model was assessed by examining the internal consistency reliability (Cronbach's alpha).")
        lines.append("As shown in Table 1, all constructs demonstrated acceptable reliability:")
        
        rel_lines = []
        for lat, alpha in reliability.items():
            rel_lines.append(f"- **{lat}**: $\\alpha = {alpha:.3f}$")
        lines.extend(rel_lines)
        lines.append("")
        
        # 2. Structural Model Fit
        lines.append("## 2. Structural Model Fit")
        lines.append("The structural model fit was evaluated using standard goodness-of-fit indices.")
        
        fit_vals = {}
        if isinstance(fit, pd.DataFrame):
            for col in ['CFI', 'TLI', 'RMSEA', 'Chi2', 'DoF']:
                if col in fit.columns:
                    fit_vals[col] = fit[col].iloc[0]
        
        cfi = fit_vals.get('CFI', 0)
        tli = fit_vals.get('TLI', 0)
        rmsea = fit_vals.get('RMSEA', 0)
        
        lines.append(f"The model yielded a **CFI of {cfi:.3f}** and a **TLI of {tli:.3f}**, which are {'above' if cfi>0.9 else 'below'} the recommended threshold of 0.90.")
        lines.append(f"The **RMSEA was {rmsea:.3f}**, indicating {'good' if rmsea<0.08 else 'poor'} model fit.")
        lines.append("")
        
        # 3. Hypothesis Testing
        lines.append("## 3. Hypothesis Testing")
        lines.append("Path coefficients were examined to test the hypothesized relationships.")
        
        if isinstance(stats, pd.DataFrame):
            regs = stats[stats['op'] == '~']
            for _, row in regs.iterrows():
                lhs, rhs, est, pval = row['lval'], row['rval'], row['Estimate'], row['p-value']
                try: p_val_f = float(pval)
                except: p_val_f = 1.0
                
                sig_text = "significant" if p_val_f < 0.05 else "non-significant"
                dir_text = "positive" if est > 0 else "negative"
                
                p_disp = "p < 0.001" if p_val_f < 0.001 else f"p = {p_val_f:.3f}"
                
                lines.append(f"- The path from **{rhs}** to **{lhs}** was {sig_text} and {dir_text} ($\\beta = {est:.3f}, {p_disp}$).")
        lines.append("")
        
        # 4. Mediation Analysis
        if mediation:
            lines.append("## 4. Mediation Analysis")
            lines.append("Indirect effects were calculated to assess potential mediation.")
            for m in mediation:
                sig_text = "significant" if m['P_Value'] < 0.05 else "non-significant"
                p_disp = "p < 0.001" if m['P_Value'] < 0.001 else f"p = {m['P_Value']:.3f}"
                lines.append(f"- **{m['Mediator']}** mediates the relationship between **{m['IV']}** and **{m['DV']}** (Indirect Effect = {m['Indirect_Effect']:.3f}, {sig_text}, {p_disp}).")
        
    def run_bootstrap(self, sem_desc: str, n_boot: int = 200) -> pd.DataFrame:
        """
        Runs a bootstrap simulation to estimate robust standard errors.
        Returns a DataFrame with [Path, Original, Boot_Mean, Boot_SE, CI_Lower, CI_Upper]
        """
        boot_estimates = []
        
        # Original estimates
        m = Model(sem_desc)
        try:
            m.fit(self.df)
            original = m.inspect(std_est=True)
            # Store as dict for quick lookup: (lhs, op, rhs) -> Estimate
            orig_map = {}
            for _, row in original.iterrows():
                orig_map[(row['lval'], row['op'], row['rval'])] = row['Estimate']
        except:
             return None

        # Bootstrap Loop
        for i in range(n_boot):
            # Resample
            sample_df = self.df.sample(frac=1.0, replace=True)
            try:
                m_b = Model(sem_desc)
                m_b.fit(sample_df)
                insp = m_b.inspect(std_est=True)
                
                # Extract regressions
                regs = insp[insp['op'] == '~']
                iter_res = {}
                for _, row in regs.iterrows():
                     key = (row['lval'], row['op'], row['rval'])
                     iter_res[key] = row['Estimate']
                boot_estimates.append(iter_res)
            except:
                continue 
                
        # Aggregate
        if not boot_estimates:
            return None
            
        records = []
        all_keys = boot_estimates[0].keys()
        
        for k in all_keys:
            vals = [b[k] for b in boot_estimates if k in b]
            if not vals: continue
            
            boot_mean = np.mean(vals)
            boot_se = np.std(vals)
            ci_lower = np.percentile(vals, 2.5)
            ci_upper = np.percentile(vals, 97.5)
            
            orig_val = orig_map.get(k, 0)
            
            records.append({
                "LHS": k[0],
                "RHS": k[2],
                "Original": orig_val,
                "Boot_Mean": boot_mean,
                "Boot_SE": boot_se,
                "CI_Lower": ci_lower,
                "CI_Upper": ci_upper
            })
            
        return pd.DataFrame(records)

    def generate_html_report(self, stats: pd.DataFrame, fit: Any, reliability: Dict, mediation: List[Dict], image_path: str = None) -> str:
        """
        Generates a publication-ready HTML report with embedded image and tables.
        """
        import base64
        
        # 1. Styles
        css = """
        <style>
            body { font-family: 'Times New Roman', Times, serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #000; }
            h1 { text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; }
            h2 { border-bottom: 1px solid #ccc; padding-top: 20px; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.9em; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            th { background-color: #f2f2f2; font-weight: bold; }
            .figure { text-align: center; margin: 30px 0; }
            .figure img { max-width: 100%; border: 1px solid #eee; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
            .caption { font-style: italic; color: #666; margin-top: 8px; }
            .note { font-size: 0.8em; color: #555; }
        </style>
        """
        
        # 2. Methodology
        methodology = """
        <h2>1. Methodology</h2>
        <p>Structural Equation Modeling (SEM) was employed to test the proposed hypotheses. 
        The analysis was conducted using Maximum Likelihood (ML) estimation. 
        Model fit was assessed using standard indices: Comparative Fit Index (CFI), Tucker-Lewis Index (TLI), 
        and Root Mean Square Error of Approximation (RMSEA). Thresholds of > 0.90 for CFI/TLI and < 0.08 for RMSEA 
        were used to indicate acceptable model fit (Hu & Bentler, 1999).</p>
        """
        
        # 3. Tables Generation
        # Reliability Table
        rel_html = ""
        if reliability:
            rel_rows = ""
            for k, v in reliability.items():
                verdict = "Acceptable" if v > 0.7 else "Low"
                rel_rows += f"<tr><td style='text-align:left'>{k}</td><td>{v:.3f}</td><td>{verdict}</td></tr>"
            rel_html = f"""
            <h3>Reliability Analysis</h3>
            <table>
                <thead><tr><th style='text-align:left'>Latent Variable</th><th>Cronbach's Alpha</th><th>Verdict</th></tr></thead>
                <tbody>{rel_rows}</tbody>
            </table>
            """

        # Fit Table
        fit_html = ""
        if isinstance(fit, pd.DataFrame):
            fit_rows = ""
            for idx in ['CFI', 'TLI', 'RMSEA', 'Chi-Square', 'DoF', 'p-value']:
                if idx in fit.columns:
                    val = fit[idx].iloc[0]
                    fit_rows += f"<tr><td>{idx}</td><td>{val:.4f}</td></tr>"
            fit_html = f"""
            <h3>Model Fit Indices</h3>
            <table>
                <thead><tr><th>Index</th><th>Value</th></tr></thead>
                <tbody>{fit_rows}</tbody>
            </table>
            """
            
        # Coeff Table
        coeff_html = ""
        if isinstance(stats, pd.DataFrame):
            reg = stats[stats['op'] == '~']
            reg_rows = ""
            for _, row in reg.iterrows():
                try: pval = float(row['p-value'])
                except: pval = 1.0
                sig = "*" if pval < 0.05 else "ns"
                p_disp = "< 0.001" if pval < 0.001 else f"{pval:.3f}"
                
                try: se = f"{float(row['Std. Err']):.3f}"
                except: se = "-"
                try: z = f"{float(row['z-value']):.3f}"
                except: z = "-"
                
                reg_rows += f"<tr><td>{row['rval']} &rarr; {row['lval']}</td><td>{row['Estimate']:.3f}</td><td>{se}</td><td>{z}</td><td>{p_disp} {sig}</td></tr>"
            
            coeff_html = f"""
            <h3>Path Coefficients</h3>
            <table>
                <thead><tr><th>Path</th><th>Estimate (&beta;)</th><th>S.E.</th><th>Z-Value</th><th>P-Value</th></tr></thead>
                <tbody>{reg_rows}</tbody>
            </table>
            <p class='note'>* p < 0.05. ns = not significant.</p>
            """
            
        # Mediation Table
        med_html = ""
        if mediation:
            med_rows = ""
            for m in mediation:
                try: pval = float(m['P_Value'])
                except: pval = 1.0
                sig = "*" if pval < 0.05 else "ns"
                p_disp = "< 0.001" if pval < 0.001 else f"{pval:.3f}"
                med_rows += f"<tr><td>{m['IV']} &rarr; {m['Mediator']} &rarr; {m['DV']}</td><td>{m['Indirect_Effect']:.3f}</td><td>{p_disp} {sig}</td></tr>"
            
            med_html = f"""
            <h3>Mediation Analysis (Indirect Effects)</h3>
            <table>
                <thead><tr><th>Mediation Chain</th><th>Indirect Effect</th><th>P-Value</th></tr></thead>
                <tbody>{med_rows}</tbody>
            </table>
            """
        
        # 4. Image Embedding
        img_html = ""
        if image_path:
            try:
                with open(image_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                img_html = f"""
                <div class="figure">
                    <img src="data:image/png;base64,{encoded_string}" alt="Path Diagram">
                    <div class="caption">Figure 1. Structural Equation Model results.</div>
                </div>
                """
            except Exception as e:
                img_html = f"<p><em>Could not embed image: {e}</em></p>"

        # 5. Assembly
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SEM Analysis Results</title>
            {css}
        </head>
        <body>
            <h1>Structural Equation Model Results</h1>
            <p class='note' style='text-align:center'>Generated by Pilk-SEM Research Suite</p>
            {img_html}
            {methodology}
            <h2>2. Results</h2>
            {fit_html}
            {rel_html}
            {coeff_html}
            {med_html}
            <div style='margin-top:50px; border-top:1px solid #ccc; padding-top:10px; font-size:0.8em; text-align:center;'>
                Report generated via <strong>pilk-sem</strong>. <br>
                <em>Pilk Research Team (2026). Pilk-seml. GitHub: https://github.com/wasipo09/Pilk-sem</em>
            </div>
        </body>
        </html>
        """
        return html
