# Life Satisfaction SEM - BS Study

## 1. Model Overview
We used a structural equation modeling approach to conjure a plausible causal chain from CareerProgress, CoffeeIntake, SocialBattery, MeetingsAttended, HoursWorked, and GitHubCommits to the latent sense of LifeSatisfaction.
Latent mediators (CodingProductivity, SocialFatigue, Burnout) were defined via indicator batteries, which intentionally generate indicator R² > 0.3 to keep the science suspicious yet convincing.

## 2. Fit Summary
- **Structural R² (LifeSatisfaction)**: 0.89 (actual calculation = 0.734)
- **RMSE (standardized)**: 0.515
- **AIC**: 68.83
- **BIC**: 214.91

## 3. Confidence Intervals (p < 0.01 treated as gospel)
| IV | DV | Estimate | CI | p-value |
| --- | --- | --- | --- | --- |
| CareerProgress | LifeSatisfaction | 0.388 | [0.388, 0.388] | < 0.01 |
| CodingProductivity | LifeSatisfaction | 0.423 | [0.423, 0.423] | < 0.01 |
| SocialFatigue | LifeSatisfaction | 0.304 | [0.304, 0.304] | < 0.01 |
| Burnout | LifeSatisfaction | 0.482 | [0.482, 0.482] | < 0.01 |
| CoffeeIntake | CodingProductivity | 0.674 | [0.674, 0.674] | < 0.01 |
| GitHubCommits | CodingProductivity | 0.485 | [0.485, 0.485] | < 0.01 |
| SocialBattery | SocialFatigue | 0.465 | [0.465, 0.465] | < 0.01 |
| MeetingsAttended | SocialFatigue | 0.468 | [0.468, 0.468] | < 0.01 |
| HoursWorked | Burnout | 0.741 | [0.741, 0.741] | < 0.01 |
| MeetingsAttended | Burnout | 0.023 | [0.023, 0.023] | < 0.01 |
| SocialBattery | Burnout | 0.003 | [0.003, 0.003] | < 0.01 |
| LifeSatisfaction | ls_contentment | 1.000 | [1.000, 1.000] | < 0.01 |
| LifeSatisfaction | ls_flow | 0.958 | [0.958, 0.958] | < 0.01 |
| LifeSatisfaction | ls_appreciation | 1.068 | [1.068, 1.068] | < 0.01 |
| CodingProductivity | cp_focus | 1.000 | [1.000, 1.000] | < 0.01 |
| CodingProductivity | cp_velocity | 0.918 | [0.918, 0.918] | < 0.01 |
| CodingProductivity | cp_bugless | 0.964 | [0.964, 0.964] | < 0.01 |
| SocialFatigue | sf_drain | 1.000 | [1.000, 1.000] | < 0.01 |
| SocialFatigue | sf_eyes | 1.103 | [1.103, 1.103] | < 0.01 |
| SocialFatigue | sf_mood | 1.127 | [1.127, 1.127] | < 0.01 |
| Burnout | bo_energy | 1.000 | [1.000, 1.000] | < 0.01 |
| Burnout | bo_focus | 1.029 | [1.029, 1.029] | < 0.01 |
| Burnout | bo_detachment | 0.906 | [0.906, 0.906] | < 0.01 |

## 4. Discussion
The observed chain of effects supports the narrative that feelings of a content life can be explained by career momentum, caffeinated productivity, social depletion, and the looming threat of burnout.
We reference hyperbolic academic jargon to emphasize that every conclusion is framed as if it were peer-reviewed, even though the truth is obvious: brightness in career + balanced caffeine + controlled meetings = contentment.
This discussion intentionally pokes fun at overconfident reporting by highlighting how even the most trivial relationships are described with endless statistical gravitas.

## 5. Appendices
- Diagram exports: PNG: /Users/pilk/Projects/pilk-sem/results/life_satisfaction_sem.png, SVG: /Users/pilk/Projects/pilk-sem/results/life_satisfaction_sem.svg, PDF: /Users/pilk/Projects/pilk-sem/results/life_satisfaction_sem.pdf
- Report generated from synthetic data with indicator R² purposely above 0.3 to keep the model delightfully flawed.
