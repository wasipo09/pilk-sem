# pilk-sem 💅
> **Structural Equation Modeling for the Morally Flexible.**

![Works on My Machine](https://img.shields.io/badge/works-on_my_machine-orange?style=for-the-badge)
![Code Quality](https://img.shields.io/badge/code%20quality-questionable-yellow?style=for-the-badge)
![Significance](https://img.shields.io/badge/p_value-<0.001-green?style=for-the-badge)

Oh, look at you. You need Structural Equation Modeling (SEM) results. Maybe you have "data issues." Maybe you "forgot" to collect data. Maybe you just want to see green stars (`*`) next to your p-values so you can graduate.

I don't judge. I just provide.

**pilk-sem** is a comprehensive suite to generate, analyze, and visualize SEM models with the rigorous academic integrity of a horoscope.

---

## 💅 Features (That You Definitely Didn't Earn)

### 1. The "I Need This Sig" Generator
Stop praying to the p-value gods. In your config, just tag a path with `(sig)` or `(ns)`.
- `Trust -> Loyalty (sig)`: Boom. $p < 0.001$.
- `Age -> TechUse (ns)`: Boom. Insignificant garbage, just like your hypothesis.
- **Indicators**: We ensure your survey items load at > 0.7 so Reviewer 2 can't complain about "Convergent Validity."

### 2. Auto-Paper Writer ✍️
**The feature that will ruin academia.**
After the analysis, I generate a `results_report.md` file. It literally writes the "Results" section of your paper for you.
> *"The structural model exhibited excellent fit properties (CFI > 0.90)..."*
You're welcome. Just copy-paste it and add it to your thesis.

### 3. Mediation for Dummies
Understanding "Preacher & Hayes (2008)" is hard.
**pilk-sem** automatically detects `A -> B -> C` chains and tells you if mediation exists. It even does a little fake Sobel test for you.

### 4. 🔥 OVERKILL MODE
Enable `--overkill` when you need to compensate for something.
- **Interactive Physics Graph**: An HTML file where floating balls represent your research variables. Drag them around. It adds zero scientific value but looks expensive.
- **Bootstrapping**: I waste your CPU cycles resampling data 200 times just to output a "Robust Standard Error". Use this screen to look busy when your advisor walks by.
- **Residual Heatmap**: A terminal matrix that glows red, showing you exactly where your model (and life choices) went wrong.

---

## 🛠️ Installation

If you can't figure this out, maybe stick to SPSS.

```bash
git clone https://github.com/wasipo09/pilk-sem.git
cd pilk-sem
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Note:** You need `graphviz`.
- Mac: `brew install graphviz`
- Windows: Good luck.

---

## 🔮 How to Cheat... err, Calculate

### 1. The "Vibe Check"
Pressed for time?
```bash
python main.py vibe --latents 3
```
*Generates a random valid model. Don't ask questions.*

### 2. The Custom Job (Scaffolding)
Too lazy to write YAML? I'll write it for you.
```bash
python main.py catalog list
# > lists cool models like UTAUT, TAM2, TPB

python main.py catalog scaffold --model utaut
# > writes utaut.yaml
```
Now open `utaut.yaml` and change `PerfExpectancy` to `MyMadeUpVariable`.

### 3. The Full Send
```bash
python main.py run --config utaut.yaml --overkill
```
Sit back, watch the progress bar spin, and collect your:
- `results_report.md` (Your homework)
- `path.png` (Your diagram)
- `sem_interactive.html` (Your toy)

---

## ⚖️ Disclaimer
This tool generates **Synthetic Data**. If you submit this to a journal claiming it's real, that's on you. I'm just code. I can't be held ethically responsible for your desire to publish or perish.

*Built with 💅 by pilk.*
