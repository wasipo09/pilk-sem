import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import run_optimization_pipeline
from visualizer import Visualizer


def test_optimization_pipeline_writes_csvs_to_output_dir(tmp_path):
    df = pd.DataFrame({"x1": [1, 2, 3], "x2": [2, 3, 4]})
    latent_map = {"Factor": ["x1", "x2"]}

    run_optimization_pipeline(df, latent_map, output_dir=tmp_path)

    assert (tmp_path / "1_raw_data.csv").exists()
    assert (tmp_path / "2_efa_cut_data.csv").exists()
    assert (tmp_path / "3_reliability_cut_data.csv").exists()


def test_visualizer_renders_diagram_inside_output_dir(tmp_path, monkeypatch):
    rendered_paths = []

    class FakeDigraph:
        def __init__(self, *args, **kwargs):
            pass

        def attr(self, *args, **kwargs):
            pass

        def node(self, *args, **kwargs):
            pass

        def edge(self, *args, **kwargs):
            pass

        def render(self, filename, format="png", cleanup=True):
            rendered = f"{filename}.{format}"
            rendered_paths.append(rendered)
            return rendered

    monkeypatch.setattr("visualizer.graphviz.Digraph", FakeDigraph)

    viz = Visualizer(filename="path", output_dir=tmp_path)
    result = viz.generate_diagram({"F1": ["x1", "x2"]}, ["F1 -> Outcome"])

    assert result == {"png": str(tmp_path / "path.png")}
    assert rendered_paths == [str(tmp_path / "path.png")]
