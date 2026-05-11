# MIMMC2026 Q3 — Generalized Bass Diffusion Model GUI

This Streamlit application simulates the future global robot vacuum cleaner market using the Generalized Bass Diffusion Model (GBDM).

The model follows the mentor-provided mathematical framework for MIMMC2026 Question 3.

---

# Mathematical Model

## Generalized Bass Diffusion Model

dN/dt = (p + qN/M)(M - N)X(t)

Where:

- N(t) = cumulative adopters
- M = market potential
- p = innovation coefficient
- q = imitation coefficient
- X(t) = intervention / marketing effort function

---

# Intervention Function

X(t) = 1 + α(dP/P) + β(dA/A) + γ(dQ/Q)

Where:

- α = price elasticity coefficient
- β = advertising elasticity coefficient
- γ = technology quality coefficient

---

# Market Potential

M = H_total × f_urban × f_suitability × f_affordability

Where:

- H_total = global households
- f_urban = urban/suburban/rural segment
- f_suitability = flooring × dwelling × cleaning need
- f_affordability = affordability factor

---

# Segments

1. Urban Apartment — Basic
2. Urban Apartment — Advanced
3. Urban Landed — Basic
4. Urban Landed — Advanced
5. Suburban Landed — Basic
6. Suburban Landed — Advanced
7. Rural Landed — Basic
8. Rural Landed — Advanced

---

# Features

The GUI allows users to:

- Change GBDM parameters
- Change affordability
- Change flooring suitability
- Change dwelling suitability
- Change cleaning need
- Change advertisement impact
- Change technology impact
- Change price elasticity (including negative alpha)
- Run Monte Carlo simulation
- Run sensitivity analysis
- Compare all segments
- Generate final AHP recommendation

---

# Files

Upload these files to GitHub:

- app.py
- requirements.txt
- README.md

---

# Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py