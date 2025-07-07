
### REVIEW THIS: https://github.com/pymc-labs/pymc-marketing/blob/0f23afc5f025bce956caebc704e4d6ac26ebaef8/pymc_marketing/mmm/base.py

## investigate impact of MMM on these
## https://www.pymc-marketing.io/en/stable/notebooks/mmm/mmm_example.html
## ROAs
# https://www.pymc-marketing.io/en/stable/notebooks/mmm/mmm_example.html#roas





import pandas as pd
import numpy as np
import arviz as az
from pymc_marketing.mmm import MMM, GeometricAdstock, LogisticSaturation
from pymc_marketing.mmm.transformers import geometric_adstock, logistic_saturation
from pymc_marketing.prior import Prior
import warnings
import random
warnings.filterwarnings("ignore", category=FutureWarning)



def create_mmm(
    start_date: str = "2018-04-01",
    end_date: str = "2021-09-01",
    channel_params: list[dict] = None,
    n_events: int = 2,
    event_dates: list[pd.Timestamp] = None,
    event_effects: list[float] = None,
    intercept: float = 2.0,
    noise_scale: float = 0.25,
    seasonality_amplitude: float = 0.5,
    yearly_seasonality: int = 2,
    model_config: dict = None,
    sampler_config: dict = None,
    seed: int = 42,
) -> dict:
    """
    Build, fit, and summarize a marketing mix model.

    Parameters:
    - start_date, end_date: date range for weekly data (freq='W-MON').
    - channel_params: list of dicts with keys:
        'name' (str), 'alpha' (float), 'saturation_lambda' (float), 'beta' (float).
      Default: two channels x1 and x2 mirroring original behavior.
    - n_events: number of one-off events to simulate (random if event_dates not provided).
    - event_dates: list of timestamps for events. If None, sampled uniformly.
    - event_effects: list of effect magnitudes per event. Default all 1.0.
    - intercept: constant term in outcome.
    - noise_scale: standard deviation of additive Gaussian noise.
    - seasonality_amplitude: amplitude multiplier for yearly seasonality term.
    - yearly_seasonality: number of Fourier pairs for seasonality in MMM.
    - model_config: PyMC-Marketing model_config dict. If None, uses sensible defaults.
    - sampler_config: PyMC-Marketing sampler_config dict. If None, uses {'progressbar': True}.
    - seed: random seed for reproducibility.

    Returns:
    A dict with keys:
    - 'channel_contribution_over_time'
    - 'channel_contribution_pass_forward_grid'
    - 'channel_contribution_barchart'
    """
    rng = np.random.default_rng(seed)

    # Prepare date frame
    dates = pd.date_range(start=start_date, end=end_date, freq='W-MON')
    df = pd.DataFrame({'date_week': dates})
    df['dayofyear'] = df['date_week'].dt.dayofyear
    n = len(df)

    # Default channels if not provided
    if channel_params is None:        
        channel_names = random.sample(['Google Ads', 'Meta Ads','TV','Radio','Website','Page Search'], 2)
        
        channel_params = [
            {'name': channel_names[0], 'alpha': 0.4, 'saturation_lambda': 4.0, 'beta': 3.0},
            {'name': channel_names[1], 'alpha': 0.2, 'saturation_lambda': 3.0, 'beta': 2.0},
        ]

    # Generate media channels
    for ch in channel_params:
        name = ch['name']
        raw = rng.uniform(0, 1, size=n)
        df[name] = raw
        # Adstock
        ad = geometric_adstock(x=raw, alpha=ch['alpha'], l_max=8, normalize=True).eval().flatten()
        df[f"{name}_adstock"] = ad
        # Saturation
        sat = logistic_saturation(x=ad, lam=ch['saturation_lambda']).eval()
        df[f"{name}_adstock_saturated"] = sat

    # Trend term
    df['t'] = np.arange(n)
    df['trend'] = (np.linspace(0, 50, n) + 10) ** (1/4) - 1

    # Yearly seasonality
    df['cs'] = -np.sin(2 * np.pi * df['dayofyear'] * 2 / 365.5)
    df['cc'] = np.cos(2 * np.pi * df['dayofyear'] * 1 / 365.5)
    df['seasonality'] = seasonality_amplitude * (df['cs'] + df['cc'])

    # Events
    if event_dates is None:
        sampled = rng.choice(df['date_week'], size=n_events, replace=False)
        event_dates = list(sampled)
    if event_effects is None:
        event_effects = [1.0] * n_events

    for i, (ed, eff) in enumerate(zip(event_dates, event_effects), start=1):
        col = f"event_{i}"
        df[col] = np.where(df['date_week'] == ed, eff, 0.0)

    # Build response y
    eps = rng.normal(0, noise_scale, size=n)
    media_term = sum(
        ch['beta'] * df[f"{ch['name']}_adstock_saturated"] for ch in channel_params
    )
    event_term = sum(df[f"event_{i+1}"] for i in range(n_events))
    df['y'] = intercept + df['trend'] + df['seasonality'] + event_term + media_term + eps

    # Prepare X and y
    drop_cols = ['y', 'dayofyear', 'cs', 'cc']
    X = df.drop(columns=drop_cols)
    y = df['y']

    # Default priors and sampler
    if model_config is None:
        total_spend = X[[ch['name'] for ch in channel_params]].sum()
        spend_share = total_spend / total_spend.sum()
        prior_sigma = len(channel_params) * spend_share.to_numpy()
        
        model_config = {
            'intercept': Prior('Normal', mu=0.5, sigma=0.2),
            'saturation_beta': Prior('HalfNormal', sigma=prior_sigma),
            'gamma_control': Prior('Normal', mu=0, sigma=0.05),
            'gamma_fourier': Prior('Laplace', mu=0, b=0.2),
            'likelihood': Prior('Normal', sigma=Prior('HalfNormal', sigma=6)),
        }
    if sampler_config is None:
        sampler_config = {'progressbar': False}

    # Instantiate and fit MMM
    mmm = MMM(
        model_config=model_config,
        sampler_config=sampler_config,
        date_column='date_week',
        adstock=GeometricAdstock(l_max=8),
        saturation=LogisticSaturation(),
        channel_columns=[ch['name'] for ch in channel_params],
        control_columns=[f"event_{i}" for i in range(1, n_events+1)] + ['t'],
        yearly_seasonality=yearly_seasonality,
    )

    mmm.sample_prior_predictive(X, y, samples=2000)
    mmm.fit(X=X, y=y, chains=4, target_accept=0.85, nuts_sampler='numpyro', random_seed=rng)
    mmm.sample_posterior_predictive(X, extend_idata=True, combined=True)

    # Summaries
    # Pass-forward grid
    grid = mmm.get_channel_contributions_forward_pass_grid(start=0, stop=1.5, num=10)
    pass_forward = {'x_axis': [str(i) for i in np.linspace(0, 1.5, 10).round(2)]}
    
    for ch in channel_params:
        total = grid.sel(channel=ch['name']).sum(dim='date')
        hdi = az.hdi(ary=total).x
        pass_forward[ch['name']] = {
            'values': total.mean(dim=('chain','draw')).values.round(2).tolist(),
            'lower': hdi[:, 0].values.round(2).tolist(),
            'upper': hdi[:, 1].values.round(2).tolist(),
        }

    # Over time
    all_time = mmm.compute_mean_contributions_over_time(original_scale=True)
    groups = {
        'Base': [f'event_{i}' for i in range(1, n_events+1)] + ['intercept', 't', 'yearly_seasonality'],
    }
    for ch in channel_params:
        groups[f"Channel {ch['name']}"] = [ch['name']]
    buff = [all_time[cols].sum(axis='columns').rename(name) for name, cols in groups.items()]
    df_time = pd.concat(buff, axis=1).reset_index()
    over_time = {
        'date': [d.strftime('%Y-%m-%d') for d in df_time['date'].tolist()],
        'values': [df_time[col].round(2).tolist() for col in df_time.columns if col != 'date'],
        'labels': [col for col in df_time.columns if col != 'date'],
    }

    # Bar chart
    decomp = mmm.compute_mean_contributions_over_time(original_scale=True)
    decomp = mmm._process_decomposition_components(data=decomp)
    barchart = {
        'labels': decomp['component'].tolist(),
        'values': decomp['contribution'].round(2).tolist(),
    }

    return {
        'channel_contribution_pass_forward_grid': pass_forward,
        'channel_contribution_over_time': over_time,
        'channel_contribution_barchart': barchart,
    }
