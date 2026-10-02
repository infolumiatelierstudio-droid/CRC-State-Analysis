"""State-level colorectal cancer (CRC) burden vs. socioeconomic factors.
Reads data/CRC_RESULT.csv, prints correlations, saves scatter plots to charts/."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv("data/CRC_RESULT.csv")
# Puerto Rico has mortality recorded as 0.00 (missing), so exclude it
df = df[(df.crc_mortality_rate > 0) & (df.state_area != "Puerto Rico")]

ABBR = {"Mississippi":"MS","Massachusetts":"MA","West Virginia":"WV","Kentucky":"KY","Louisiana":"LA",
        "Arkansas":"AR","Texas":"TX","Vermont":"VT","District of Columbia":"DC","California":"CA",
        "Hawaii":"HI","Maine":"ME","Florida":"FL","Utah":"UT","Colorado":"CO","Connecticut":"CT","New Jersey":"NJ"}

ANALYSES = [  # (file, x col, x label, y col, y label, labelled states)
 ("income_vs_mortality","median_household_income","Median household income ($)","crc_mortality_rate","CRC mortality per 100k",["Mississippi","Massachusetts","West Virginia","Connecticut","New Jersey"]),
 ("uninsured_vs_late_stage","uninsured_under_65_pct","Uninsured under 65 (%)","late_stage_crc_rate","Late-stage CRC rate",["Texas","Mississippi","Massachusetts","Vermont","District of Columbia"]),
 ("stool_test_vs_mortality","home_stool_test_pct","Home stool test use (%)","crc_mortality_rate","CRC mortality per 100k",["California","Hawaii","Mississippi","Kentucky"]),
 ("poverty_vs_incidence","persons_below_poverty_pct","Persons below poverty (%)","crc_incidence_rate","CRC incidence per 100k",["Mississippi","Louisiana","West Virginia","Massachusetts"]),
 ("poverty_vs_mortality","persons_below_poverty_pct","Persons below poverty (%)","crc_mortality_rate","CRC mortality per 100k",["Mississippi","Louisiana","West Virginia","Massachusetts"]),
 ("education_vs_mortality","bachelors_or_more_pct","Bachelor's degree or more (%)","crc_mortality_rate","CRC mortality per 100k",["Mississippi","West Virginia","Massachusetts","Colorado"]),
 ("age_vs_incidence","population_65_plus_pct","Population 65+ (%)","crc_incidence_rate","CRC incidence per 100k",["Kentucky","Mississippi","West Virginia","Maine","Florida","Utah"]),
]
rows = []
for name, x, xl, y, yl, hl in ANALYSES:
    r, p = stats.pearsonr(df[x], df[y]); rho = stats.spearmanr(df[x], df[y])[0]
    rows.append((name, round(r,2), round(p,4), round(rho,2)))
    fig, ax = plt.subplots(figsize=(6,4.2))
    ax.scatter(df[x], df[y], s=18, color="#8aa3b3", alpha=.8)
    m, c = np.polyfit(df[x], df[y], 1); xs = np.linspace(df[x].min(), df[x].max(), 50)
    ax.plot(xs, m*xs+c, "--", color="#0b6e7f", lw=1.5)
    for s in hl:
        q = df[df.state_area == s].iloc[0]
        ax.scatter(q[x], q[y], color="#c2410c", s=36); ax.annotate(ABBR[s], (q[x], q[y]), xytext=(4,4), textcoords="offset points", fontsize=8, weight="bold")
    ax.set(xlabel=xl, ylabel=yl, title=f"{xl.split(' (')[0]} vs {yl.split(' per')[0]}  (r = {r:+.2f})")
    ax.spines[["top","right"]].set_visible(False); fig.tight_layout(); fig.savefig(f"charts/{name}.png", dpi=150); plt.close(fig)

print(pd.DataFrame(rows, columns=["analysis","pearson_r","p_value","spearman_rho"]).to_string(index=False))

# Age-adjusted excess incidence: residual from incidence ~ % 65+
m, c = np.polyfit(df.population_65_plus_pct, df.crc_incidence_rate, 1)
df = df.assign(excess_incidence=df.crc_incidence_rate - (m*df.population_65_plus_pct + c))
print(df.sort_values("excess_incidence", ascending=False)[["state_area","excess_incidence"]].head(8).round(1).to_string(index=False))
