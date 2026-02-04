
import graphviz
from typing import Dict, List, Optional

class Visualizer:
    def __init__(self, filename="path"):
        self.filename = filename
        
    def generate_diagram(self, latents: Dict[str, List[str]], paths: List[str], stats=None):
        """
        Generates an AMOS-style path diagram.
        """
        dot = graphviz.Digraph(comment='SEM Path Diagram')
        dot.attr(rankdir='LR')
        dot.attr('node', style='filled', fillcolor='white', fontname='Helvetica')
        
        # Identify all structural nodes
        all_structural_nodes = set()
        for p in paths:
            if '->' in p:
                src, dst = p.split('->')
                all_structural_nodes.add(src.strip())
                all_structural_nodes.add(dst.strip())
                
        # 1. Add Latent Nodes (Ellipses)
        for latent in latents.keys():
            dot.node(latent, latent, shape='ellipse', penwidth='2')
            if latent in all_structural_nodes:
                all_structural_nodes.remove(latent)
                
        # 2. Add Observed Structural Nodes (Rectangles) - e.g. Controls or directly observed
        for obs in all_structural_nodes:
             dot.node(obs, obs, shape='box', penwidth='1.5')
            
        # 3. Add Indicator Nodes (Rectangles) for Latents
        dot.attr('node', shape='box', style='filled', fillcolor='yellow:white', gradientangle='270', penwidth='1')
        for latent, indicators in latents.items():
            for ind in indicators:
                dot.node(ind, ind)
                # Edge from Latent to Indicator
                label = ""
                dot.edge(latent, ind, label=label)
                
                # Add Error term for indicator
                err_name = f"e_{ind}"
                dot.node(err_name, "e", shape='circle', width='0.3', fixedsize='true', fontsize='10', fillcolor='white')
                dot.edge(err_name, ind)

        # 4. Add Structural Paths
        dot.attr('edge', penwidth='1.5')
        for p in paths:
            if '->' in p:
                src, dst = p.split('->')
                src, dst = src.strip(), dst.strip()
                dot.edge(src, dst)
                
                # Add disturbance for endogenous latent?
                # Usually yes, but simplify for now.
        
        # 4. Render
        try:
            dot.render(self.filename, format='png', cleanup=True)
            return f"{self.filename}.png"
        except graphviz.backend.ExecutableNotFound:
            return "Error: Graphviz executable 'dot' not found. Please run 'brew install graphviz' or install it for your OS."
        except Exception as e:
            return f"Error visualizing: {e}"
