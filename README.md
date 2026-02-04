# pilk-sem 🔮
> **The Ultimate Vibe-Coding SEM Suite**

![Version](https://img.shields.io/badge/version-1.0.0-gold?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.9+-CB3837?style=for-the-badge&logo=python&logoColor=white)
![Academic](https://img.shields.io/badge/academic-ready-blue?style=for-the-badge)

**pilk-sem** is a sophisticated, "batteries-included" simulation and learning suite for Structural Equation Modeling (SEM). It is designed to generate publication-quality synthetic data, perform rigorous AMOS-style analysis, and even **write your academic results section for you**.

Whether you are learning AMOS, testing a complex path model (like TAM2), or just need valid data to practice on, **pilk-sem** provides a complete ecosystem.

## ✨ Key Features

### 🧠 Intelligent Data Generation
- **Complex Structures**: Supports Latent Variables, Observed Variables, and Contol Variables in the same model.
- **Vibe Control**: Force paths to be **Significant** (`sig`) or **Non-Significant** (`ns`) to test specific hypotheses.
- **Quality Assurance**: Guaranteed "passing" indicators (loadings > 0.7) and high reliability.

### 📊 Advanced Analytics Engine
- **Full Psychometrics**: EFA (Eigenvalues), Cronbach's Alpha, and CFA.
- **Model Fit**: Calculates CFI, TLI, RMSEA, etc.
- **Mediation Analysis**: Automatically detects `A -> B -> C` chains and calculates **Indirect Effects** and significance (Sobel-like check).

### ✍️ The "Auto-Reporter"
**The feature you never knew you wanted.** After every run, **pilk-sem** generates a `results_report.md` file containing a drafted **Academic Results Section**. It interprets the stats and writes the paragraphs for you.

### 🎨 AMOS-Style Visualization
Generates `path.png` diagrams that mimic the look of AMOS (Rectangles for observed, Ellipses for latents).

---

## 🚀 Installation

1.  **Clone & Install**
    ```bash
    git clone https://github.com/yourusername/pilk-sem.git
    cd pilk-sem
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **System Requirements**
    You need **Graphviz** installed for the visualizer:
    - **Mac**: `brew install graphviz`
    - **Windows**: Download iterator from graphviz.org (add to PATH).
    - **Linux**: `sudo apt-get install graphviz`

---

## 📖 Usage Guide

### 1. The "Vibe Check" (Quick Start)
Need a random valid SEM model in 2 seconds?
```bash
python main.py vibe --latents 3 --indicators 4 --n 300
```
*Generates a simple 3-factor chain model, runs analysis, and shows you the path diagram.*

### 2. The Power User (Config Mode)
To simulate a specific study, create a YAML config file.

**Run Command:**
```bash
python main.py run --config your_model.yaml
```

**Configuration Schema (`model.yaml`):**
```yaml
sample_size: 400

# Define Latent Constructs and their Indicators
latents:
  Trust: [t1, t2, t3]
  Loyalty: [l1, l2, l3]

# Define Directly Observed Variables (optional)
observed: 
  - Age
  - Income

# Define Structural Paths
# Use (sig) to force Significance (p < 0.05)
# Use (ns) to force Non-Significance
paths:
  - Trust -> Loyalty (sig)
  - Age -> Loyalty (ns)
  - Income -> Trust (sig)

# Define Conrol Variables (optional)
controls:
  - Gender
```

---

## 🧪 Feature Demos & Samples

### Demo A: The TAM2 Model (Complex)
We have included a full **Technology Acceptance Model 2 (TAM2)** configuration. This model includes 9 Latent Variables and complex mediation.

**Run it:**
```bash
python main.py run --config tam2.yaml
```

**What to look for:**
1.  **Mediation Table**: Look at the output for "Indirect Effects". You will see chains like `SubjectiveNorm -> Image -> PU`.
2.  **Report**: Open `results_report.md`. You will see text like:
    > *"SubjectiveNorm mediates the relationship between Image and PU (Indirect Effect = 0.417, significant, p < 0.001)."*

### Demo B: Hypothesis Testing
Try `test_model.yaml` to see how we force specific p-values.
```bash
python main.py run --config test_model.yaml
```
*Check the "Regression Coefficients" table to verify that `Age -> Loyalty` is indeed non-significant (`ns`).*

---

## 📂 Project Structure

- `main.py`: CLI entry point. Configures the vibe.
- `generator.py`: The simulation engine. Handles the logic for `sig`/`ns` paths and structural equations.
- `analysis.py`: Wrap `semopy` and `factor_analyzer`. Contains the **Auto-Report** logic.
- `visualizer.py`: Uses `graphviz` to draw the diagram.
- `results_report.md`: The output file where your paper is written.
- `path.png`: The visual output.

---

## 🤝 Contributing

Feel free to fork and add more intricate models (e.g. UTAUT, PLS-SEM styles). Code is vibe-checked and ready to ship.

---
*Built with 💖 by the pilk-sem team.*
