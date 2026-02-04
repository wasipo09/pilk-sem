
import numpy as np
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional

class SyntheticDataGenerator:
    """
    Generates synthetic data for SEM analysis.
    Simulates a structural equation model with latent variables and optional controls.
    """
    def __init__(self, n_samples: int = 300, seed: int = 42):
        self.n_samples = n_samples
        self.rng = np.random.default_rng(seed)
        
    def generate_data(self, config: Dict) -> pd.DataFrame:
        """
        Generates DataFrame based on valid config dict.
        Config schema:
            sample_size: int
            latents: {Name: [ind1, ind2]}
            observed: [name1, name2]
            paths: ["A -> B (sig)", "B -> C (ns)"]
            controls: [c1, c2]
        """
        n = config.get('sample_size', self.n_samples)
        latents = config.get('latents', {})
        observed = config.get('observed', [])
        paths = config.get('paths', [])
        controls = config.get('controls', [])
        
        # 1. Initialize Storage
        data = {}
        
        # 2. Identify Variables
        latent_names = list(latents.keys())
        all_structural_nodes = latent_names + observed
        
        # Parse Paths
        # Structure: (source, target, type) where type is 'sig', 'ns', or 'default'
        edges = []
        for p in paths:
            sig_type = 'default'
            if '(sig)' in p:
                sig_type = 'sig'
                p = p.replace('(sig)', '')
            elif '(ns)' in p:
                sig_type = 'ns'
                p = p.replace('(ns)', '')
                
            if '->' in p:
                src, dst = p.split('->')
                edges.append({
                    'src': src.strip(), 
                    'dst': dst.strip(),
                    'type': sig_type
                })

        # 3. Topological Sort / Level determination (simplified)
        # Determine Endogenous vs Exogenous
        targets = {e['dst'] for e in edges}
        endogenous = targets
        exogenous = [n for n in all_structural_nodes if n not in endogenous]
        
        # 4. Generate Exogenous Variables (Latents & Observed)
        # (Assuming standard normal to start)
        for var in all_structural_nodes:
            # Initialize with random noise
            data[var] = self.rng.standard_normal(n)
            
        # 5. Generate Controls (Exogenous by definition usually)
        for c in controls:
            # Random binary or continuous
            if self.rng.random() > 0.5:
                # Binary
                data[c] = self.rng.integers(0, 2, n)
            else:
                # Continuous
                data[c] = self.rng.normal(0, 1, n)

        # 6. Apply Structural Relationships (Iterative for depth)
        # We start with the exogenous noise we generated and propagate.
        # Since we initialized everyone with noise, we treat that as the "disturbance" term for endogenous vars.
        # But for endogenous, we want Y = B*X + e. Currently Y = e.
        # So we just add B*X to the existing Y.
        
        # Sort edges to respect causal flow roughly? 
        # Multi-pass is safer for arbitrary DAGs.
        for _ in range(3):
            for edge in edges:
                src, dst, etype = edge['src'], edge['dst'], edge['type']
                
                # Determine Beta
                if etype == 'sig':
                    # Strong effect: 0.3 to 0.7
                    beta = self.rng.uniform(0.3, 0.7)
                    if self.rng.random() > 0.5: beta *= -1 # Random direction unless specified? User implies positive sig usually? Let's keep positive for "vibe" unless indicated.
                    beta = abs(beta) # Force positive for "vibe" simplicity
                elif etype == 'ns':
                    # Weak effect: -0.05 to 0.05
                    beta = self.rng.uniform(-0.05, 0.05)
                else:
                    # Default
                    beta = self.rng.uniform(0.2, 0.5)
                
                # Apply
                if src in data and dst in data:
                    data[dst] += beta * data[src]

        # 7. Apply Controls to Endogenous Vars
        # If controls are present, let's assume they affect all Endogenous vars to make 'sem with controls' meaningful
        # Or user should specify control paths? 
        # User request: "controls too" -> usually means "control for these".
        # We'll add small random effects from controls to all endogenous vars
        for c in controls:
            for endo in endogenous:
                beta_c = self.rng.uniform(0.1, 0.3)
                data[endo] += beta_c * data[c]
                
        # 8. Normalize Latents/Observed before measurement info
        # (Keeps scales consistent)
        for v in all_structural_nodes:
             data[v] = (data[v] - np.mean(data[v])) / np.std(data[v])

        # 9. Generate Indicators (Measurement Model) "All Indicators Passed" -> High Loadings
        final_data = {}
        for c in controls:
             final_data[c] = data[c]
        
        # Copy observed directly
        for obs in observed:
             val = data[obs]
             # Scale to 1-7 likely
             val = val * 1.5 + 4
             final_data[obs] = np.clip(val, 1, 7)

        # Latent Indicators
        for latent, indicators in latents.items():
            scores = data[latent]
            for ind in indicators:
                # High loading for "passed"
                loading = self.rng.uniform(0.75, 0.95)
                err = self.rng.normal(0, 0.3, n) # Low error
                
                val = loading * scores + err
                # Scale
                val = val * 1.5 + 4
                final_data[ind] = np.clip(val, 1, 7)
                
        df = pd.DataFrame(final_data)
        return df

    def save_csv(self, df: pd.DataFrame, filename: str = "mock_data.csv"):
        df.to_csv(filename, index=False)
