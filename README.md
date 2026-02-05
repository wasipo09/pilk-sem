# pilk-sem: The Vibe-Coding SEM Tool

> "Because Life Satisfaction is just a latent variable waiting to be identified."

**pilk-sem** is a Python-based Structural Equation Modeling (SEM) tool designed for researchers who are tired of clicking buttons in Amos and wondering why their model won't fit. We believe in **Vibe-Coding**: if the model feels right, the data will eventually confess.

## Why use this?
- **Automatic Data Optimization**: We don't call it "dropping items until it works," we call it *optimization*. Our multi-stage pipeline aggressively prunes your data based on EFA loadings and Reliability scores before you even see the bad news.
- **Snarky Reports**: Fit indices are color-coded so you know exactly how much shame to feel.
- **Overkill Mode**: Want to bootstrap 200 times just to feel something? We got you.
- **Interactive Physics**: Static path diagrams are boring. Throw your latent variables around a canvas like a frustrated toddler.

## Installation

```bash
# Clone this bad boy
git clone https://github.com/wasipo09/pilk-sem.git
cd pilk-sem

# Install the stuff
pip install -r requirements.txt
```

## Usage

### 1. The Vibe Check (Simulation)
Don't have data? Fake it 'til you make it. Generate synthetic data and see if your imaginary theory holds water.

```bash
python main.py vibe --latents 3 --indicators 5 --n 200
```

**What happens?**
1. We generate perfect (or slightly noisy) data.
2. **The Pipeline™** kicks in:
   - **Step 1**: Raw data is saved (`1_raw_data.csv`).
   - **Step 2**: We run an EFA. Loadings < 0.4? yeet. (`2_efa_cut_data.csv`)
   - **Step 3**: We check Reliability. Item-Total Correlation < 0.3? Gone. (`3_reliability_cut_data.csv`)
3. We run the SEM on whatever survived.
4. We verify the fit indices. (CFI > 0.9 or bust).
5. We gen an HTML report `publication_ready.html` so you can pretend you did this in R.

### 2. The Real Deal (Config File)
Got a hypothesis? Write it down in a YAML file and let us destroy it.

```bash
python main.py run --config tam2.yaml --overkill
```

**Config Format (YAML)**
```yaml
latents:
  PEOU: [x1, x2, x3]
  PU: [x4, x5, x6]
  BI: [x7, x8]

paths:
  - PEOU -> PU
  - PU -> BI
  - PEOU -> BI
```

## Features Deep Dive

### The "Optimization" Pipeline
We output CSVs at every stage of the butchery:
- `1_raw_data.csv`: The mess you started with.
- `2_efa_cut_data.csv`: After we realized `x4` didn't actually load on anything.
- `3_reliability_cut_data.csv`: After we realized `x2` was negatively correlated with its own scale.

By the time we run SEM, your data is sleek, aerodynamic, and statistically significant. (Disclaimer: Results may vary. We are not responsible for your rejection letters).

### Overkill Mode (`--overkill`)
Adds:
- **Bootstrapping**: 200 iterations of robust standard error estimation.
- **Residual Heatmaps**: See exactly where your covariance matrix is bleeding.
- **Interactive Graph**: A physics-based network graph saved as an HTML file.

## Citation
If you actually use this for a paper, first of all, **bold move**. Second, cite us:

> Pilk Research Team (2026). *pilk-sem: Automated Structural Equation Modeling with Attitude*. GitHub.

## License
MIT. Do whatever you want, just don't blame us for your RMSEA > 0.10.
