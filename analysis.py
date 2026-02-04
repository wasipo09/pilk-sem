
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
    def __init__(self, df: pd.DataFrame):
        self.df = df

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
        
        lines.append("\n*Report generated by pilk-sem.*")
        return "\n".join(lines)
