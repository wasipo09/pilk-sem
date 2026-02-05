import graphviz
from pyvis.network import Network
from typing import Dict, List, Tuple
import os

class Visualizer:
    def __init__(self, filename="path"):
        self.filename = filename
        
    def generate_interactive(self, latents: Dict[str, List[str]], paths: List[str], stats=None) -> str:
        """
        Generates an interactive HTML path diagram using pyvis.
        """
        net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white')
        net.barnes_hut()
        
        # 1. Add Nodes
        
        # Latents
        for lat in latents.keys():
            net.add_node(lat, label=lat, title=lat, color='#ffcc00', shape='dot', size=30)
            
        # Indicators & Observed
        # Identify observed variables from paths that are not latents
        all_nodes = set()
        for p in paths:
             parts = p.split('->')
             if len(parts) == 2:
                 all_nodes.add(parts[0].strip())
                 all_nodes.add(parts[1].strip())
        
        # Add indicators as nodes
        for lat, indicators in latents.items():
            for ind in indicators:
                 net.add_node(ind, label=ind, title=f"Indicator of {lat}", color='#00ccff', shape='square', size=15)
                 # Add measurement edge (grey)
                 net.add_edge(lat, ind, color='grey', width=1)
                 
        # Add pure observed variables (structurals not in latents/indicators)
        known_vars = set(latents.keys()) | {i for inds in latents.values() for i in inds}
        observed_struct = all_nodes - known_vars
        
        for obs in observed_struct:
            net.add_node(obs, label=obs, title=f"Observed: {obs}", color='#00ccff', shape='square', size=20)
            
        # 2. Add Structural Edges
        # If stats present, use p-values for color
        path_stat_map = {}
        if stats is not None:
            # Map (lhs, rhs) -> (est, pval)
            # semopy: lval ~ rval
            regs = stats[stats['op'] == '~']
            for _, row in regs.iterrows():
                path_stat_map[(row['rval'], row['lval'])] = (row['Estimate'], row['p-value'])

        for p in paths:
            if '->' not in p: continue
            src, dst = [x.strip() for x in p.split('->')]
            
            color = 'white'
            width = 2
            title = "Path"
            
            if (src, dst) in path_stat_map:
                est, pval = path_stat_map[(src, dst)]
                try: p_val_f = float(pval)
                except: p_val_f = 1.0
                
                is_sig = p_val_f < 0.05
                color = '#00ff00' if is_sig else '#444444' # Green if sig, Dark Grey if ns
                width = 1 + abs(est) * 3
                title = f"Beta={est:.3f}, p={p_val_f:.3f}"
            
            net.add_edge(src, dst, color=color, width=width, title=title)
            
        output_file = "sem_interactive.html"
        net.save_graph(output_file)
        return output_file

    def generate_diagram(self, latents: Dict[str, List[str]], paths: List[str], stats=None, output_formats=('png',)):
        """
        Generates an AMOS-style path diagram and exports to the requested formats.
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
        
        # 5. Render to requested formats
        diagrams = {}
        for fmt in output_formats:
            try:
                rendered = dot.render(self.filename, format=fmt, cleanup=True)
                diagrams[fmt] = rendered
            except graphviz.backend.ExecutableNotFound:
                diagrams[fmt] = "Error: Graphviz executable 'dot' not found. Please install graphviz."
            except Exception as e:
                diagrams[fmt] = f"Error visualizing ({fmt}): {e}"
        
        return diagrams
