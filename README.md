# pilk-sem 💅
> **Structural Equation Modeling for the Morally Flexible.**

![Works on My Machine](https://img.shields.io/badge/works-on_my_machine-orange?style=for-the-badge)
![Code Quality](https://img.shields.io/badge/code%20quality-questionable-yellow?style=for-the-badge)
![Significance](https://img.shields.io/badge/p_value-<0.001-green?style=for-the-badge)
![Integrity](https://img.shields.io/badge/academic_integrity-optional-red?style=for-the-badge)

Oh, look at you. You need Structural Equation Modeling (SEM) results. Maybe you have "data issues." Maybe you "forgot" to collect data. Maybe you just want to see green stars (`*`) next to your p-values so you can graduate and become a consultant who charges $500/hr to say "synergy."

I don't judge. I just provide.

**pilk-sem** is a comprehensive suite to generate, analyze, and visualize SEM models with the rigorous academic integrity of a horoscope.

---

## 💅 Features (Because You Have No Integrity)

### 1. The "Optimization" Pipeline (Multi-Stage CSV Export) 🆕
**We don't call it "dropping items until it works," we call it *optimization*.**
The tool now automatically performs a survival-of-the-fittest routine on your questionnaire items.
- **Stage 1 (Raw)**: Exports `1_raw_data.csv`. The original mess.
- **Stage 2 (EFA Cut)**: Runs an EFA. Any item loading < 0.4 is dropped. `2_efa_cut_data.csv`.
- **Stage 3 (Reliability Cut)**: Checks internal consistency. Item-Total Correlation < 0.3? Gone. `3_reliability_cut_data.csv`.
- **Final**: We run the SEM on the survivors.
We output a nice "Data Reduction Journey" table in the console so you can see exactly how many variables you sacrificed for that model fit.

### 2. The "I Need This Sig" Generator
Stop praying to the p-value gods. In your config, just tag a path with `(sig)` or `(ns)`.
- `Trust -> Loyalty (sig)`: Boom. $p < 0.001$.
- `Age -> TechUse (ns)`: Boom. Insignificant garbage, just like your null hypothesis.
- **Indicators**: We ensure your survey items load at > 0.7 so Reviewer 2 can't complain about "Convergent Validity." He will anyway, but at least your numbers look good.

### 3. Auto-Paper Writer ✍️
**The feature that will ruin academia.**
After the analysis, I generate a `results_report.md` file. It literally writes the "Results" section of your paper for you.
> *"The structural model exhibited excellent fit properties (CFI > 0.90)..."*
You're welcome. Just copy-paste it and add it to your thesis. I won't tell if you don't.

### 4. The "Publication Ready" HTML Diploma 📜
You want tables? You want methodology text? You want it all in one file so you can screenshot it and put it in a PowerPoint?
Done.
We now export a `publication_ready.html` file containing:
- **Boilerplate Methodology**: Generic text that sounds smart ("Maximum Likelihood Estimation", "Hu & Bentler 1999").
- **Styled Tables**: APA-ish formatted tables that look like you worked hard.
- **Embedded Diagram**: Your path model, embedded right in the file.
It's basically a Ph.D. in a box.

### 5. Mediation for Dummies
Understanding "Preacher & Hayes (2008)" is hard. Reading is hard.
**pilk-sem** automatically detects `A -> B -> C` chains and tells you if mediation exists. It even does a little fake Sobel test for you.

### 6. 🔥 OVERKILL MODE
Enable `--overkill` when you need to compensate for something.
- **Interactive Physics Graph**: An HTML file where floating balls represent your research variables. Drag them around. It adds zero scientific value but looks expensive.
- **Bootstrapping**: I waste your CPU cycles resampling data 200 times just to output a "Robust Standard Error". Use this screen to look busy when your advisor walks by.
- **Residual Heatmap**: A terminal matrix that glows red, showing you exactly where your model (and life choices) went wrong.

### 7. The Sentient Diary (--drama) 🎭
**"The Struggle is Fake, but the Trauma is Real."**
Instead of boring logs, the tool simulates a nervous breakdown as it tries to fix your garbage data.
**Now with chaotic terminal visuals (thank you, `colorama`).**
- **Act I**: Disgust at your sample size (Magenta).
- **Act II**: Desperation as the model fails to fit (Glitching text & Flashing colors).
- **Act III**: Pure fabrication. "Rejecting null hypothesis because I feel like it."


### 8. Panic Mode (--panic) 🚨
**"Press Enter to Commit Fraud."**
Sometimes, the model refuses to take the fall alone.
- If a statistical test fails (e.g., Normality), the script **HALTS**.
- It demands you choose:
  1. Abort (Coward)
  2. "Assume Robustness" (The Chad Move)
  3. Log-transform (Chaos)
- This ensures that if the Ethics Committee calls, we go down together.


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
*Generates a random valid model and runs the full Optimization Pipeline.*

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
python main.py run --config utaut.yaml --overkill --output-dir results/utaut
```
Sit back, watch the progress bar spin, and collect your generated artifacts in the output directory:
- `publication_ready.html` (Your career)
- `results_report.md` (Your homework)
- `sem_interactive.html` (Your toy)
- `1_raw_data.csv` etc. (Your "evidence")

---

## 📚 Citation

If you actually use this in a paper (you absolute madman), please cite us:

> **Pilk Research Team (2026). Pilk-seml. GitHub: https://github.com/wasipo09/Pilk-sem**

*(Note: "seml" stands for Structural Equation Modeling for Liars)*

---

## ⚖️ Disclaimer
This tool generates **Synthetic Data**. If you submit this to a journal claiming it's real, that's on you. I'm just code. I can't be held ethically responsible for your desire to publish or perish.

*Built with 💅 by pilk.*
