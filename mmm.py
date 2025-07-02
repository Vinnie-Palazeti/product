import pandas as pd
import numpy as np
from pymc_marketing.mmm import MMM, GeometricAdstock, LogisticSaturation
from pymc_marketing.mmm.transformers import geometric_adstock, logistic_saturation
from pymc_marketing.prior import Prior
import warnings
import arviz as az
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)

az.style.use("arviz-darkgrid")
plt.rcParams["figure.figsize"] = [12, 7]
plt.rcParams["figure.dpi"] = 100


seed: int = sum(map(ord, "mmm"))
rng: np.random.Generator = np.random.default_rng(seed=seed)

# date range
min_date = pd.to_datetime("2018-04-01")
max_date = pd.to_datetime("2021-09-01")

df = pd.DataFrame(
    data={"date_week": pd.date_range(start=min_date, end=max_date, freq="W-MON")}
).assign(
    year=lambda x: x["date_week"].dt.year,
    month=lambda x: x["date_week"].dt.month,
    dayofyear=lambda x: x["date_week"].dt.dayofyear,
)

n = df.shape[0]
print(f"Number of observations: {n}")

# media data
x1 = rng.uniform(low=0.0, high=1.0, size=n)
df["x1"] = np.where(x1 > 0.9, x1, x1 / 2)

x2 = rng.uniform(low=0.0, high=1.0, size=n)
df["x2"] = np.where(x2 > 0.8, x2, 0)

# apply geometric adstock transformation
alpha1: float = 0.4
alpha2: float = 0.2

df["x1_adstock"] = (
    geometric_adstock(x=df["x1"].to_numpy(), alpha=alpha1, l_max=8, normalize=True)
    .eval()
    .flatten()
)

df["x2_adstock"] = (
    geometric_adstock(x=df["x2"].to_numpy(), alpha=alpha2, l_max=8, normalize=True)
    .eval()
    .flatten()
)

# apply saturation transformation
lam1: float = 4.0
lam2: float = 3.0

df["x1_adstock_saturated"] = logistic_saturation(
    x=df["x1_adstock"].to_numpy(), lam=lam1
).eval()

df["x2_adstock_saturated"] = logistic_saturation(
    x=df["x2_adstock"].to_numpy(), lam=lam2
).eval()

df["trend"] = (np.linspace(start=0.0, stop=50, num=n) + 10) ** (1 / 4) - 1

df["cs"] = -np.sin(2 * 2 * np.pi * df["dayofyear"] / 365.5)
df["cc"] = np.cos(1 * 2 * np.pi * df["dayofyear"] / 365.5)
df["seasonality"] = 0.5 * (df["cs"] + df["cc"])
df["event_1"] = (df["date_week"] == "2019-05-13").astype(float)
df["event_2"] = (df["date_week"] == "2020-09-14").astype(float)

df["intercept"] = 2.0
df["epsilon"] = rng.normal(loc=0.0, scale=0.25, size=n)

amplitude = 1
beta_1 = 3.0
beta_2 = 2.0
betas = [beta_1, beta_2]


df["y"] = amplitude * (
    df["intercept"]
    + df["trend"]
    + df["seasonality"]
    + 1.5 * df["event_1"]
    + 2.5 * df["event_2"]
    + beta_1 * df["x1_adstock_saturated"]
    + beta_2 * df["x2_adstock_saturated"]
    + df["epsilon"]
)

columns_to_keep = [
    "date_week",
    "y",
    "x1",
    "x2",
    "event_1",
    "event_2",
    "dayofyear",
]

data = df[columns_to_keep].copy()
data["t"] = range(n)


total_spend_per_channel = data[["x1", "x2"]].sum(axis=0)
spend_share = total_spend_per_channel / total_spend_per_channel.sum()

n_channels = 2
prior_sigma = n_channels * spend_share.to_numpy()

X = data.drop("y", axis=1)
y = data["y"]

my_model_config = {
    "intercept": Prior("Normal", mu=0.5, sigma=0.2),
    "saturation_beta": Prior("HalfNormal", sigma=prior_sigma),
    "gamma_control": Prior("Normal", mu=0, sigma=0.05),
    "gamma_fourier": Prior("Laplace", mu=0, b=0.2),
    "likelihood": Prior("Normal", sigma=Prior("HalfNormal", sigma=6)),
}

my_sampler_config = {"progressbar": True}

mmm = MMM(
    model_config=my_model_config,
    sampler_config=my_sampler_config,
    date_column="date_week",
    adstock=GeometricAdstock(l_max=8),
    saturation=LogisticSaturation(),
    channel_columns=["x1", "x2"],
    control_columns=["event_1", "event_2", "t"],
    yearly_seasonality=2,
)

# Generate prior predictive samples
mmm.sample_prior_predictive(X, y, samples=2_000)



# fig, ax = plt.subplots()
# mmm.plot_prior_predictive(ax=ax, original_scale=True)
# ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=4)
# fig.show()

mmm.fit(X=X, y=y, chains=4, target_accept=0.85, nuts_sampler="numpyro", random_seed=rng)

# sample from the posterior predictive distribution
mmm.sample_posterior_predictive(X, extend_idata=True, combined=True)

# errors = mmm.get_errors(original_scale=True)
# fig, ax = plt.subplots(figsize=(8, 6))
# az.plot_dist(
#     errors, quantiles=[0.25, 0.5, 0.75], color="C3", fill_kwargs={"alpha": 0.7}, ax=ax
# )
# ax.axvline(x=0, color="black", linestyle="--", linewidth=1, label="zero")
# ax.legend()
# ax.set(title="Errors Posterior Distribution")

groups = {
    "Base": [
        "intercept",
        "event_1",
        "event_2",
        "t",
        "yearly_seasonality",
    ],
    "Channel 1": ["x1"],
    "Channel 2": ["x2"],
}

breakpoint()

fig = mmm.plot_grouped_contribution_breakdown_over_time(
    stack_groups=groups,
    original_scale=True,
    area_kwargs={
        "color": {
            "Channel 1": "C0",
            "Channel 2": "C1",
            "Base": "gray",
            "Seasonality": "black",
        },
        "alpha": 0.7,
    },
)

# fig.suptitle("Contribution Breakdown over Time", fontsize=16)
# fig.show()

all_contributions_over_time = mmm.compute_mean_contributions_over_time(original_scale=True)

if groups is not None:
    grouped_buffer = []
    for group, columns in groups.items():
        grouped = (
            all_contributions_over_time.filter(columns)
            .sum(axis="columns")
            .rename(group)
        )
        grouped_buffer.append(grouped)

    all_contributions_over_time = pd.concat(grouped_buffer, axis="columns")


mmm.plot_waterfall_components_decomposition()
plt.show()




dataframe=mmm.compute_mean_contributions_over_time(original_scale=False)
dataframe = mmm._process_decomposition_components(data=dataframe)
total_contribution = dataframe["contribution"].sum()


mmm.plot_channel_contribution_grid(start=0, stop=1.5, num=12)


