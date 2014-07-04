import numpy as np
from scipy import optimize, stats

import pwt

# load the Penn World Tables data
pwt_data = pwt.load_pwt_data()

def _technology(capital, labor, output, g, n, s, delta, rho, sigma, omega):
    """Technology as a residual of the CES production function."""
    output_per_worker = output / labor
    capital_labor_ratio = capital / labor

    if abs(rho) < 1e-3:
        tech = (output_per_worker / capital_labor_ratio**omega)**(1 / (1 - omega))
    else:
        tech = ((1 / (1 - omega)) * output_per_worker**rho + 
                (omega / (1 - omega)) * capital_labor_ratio**rho)**(1 / rho)

    return tech

def _initial_condition(ctry, params, start):
    """Initial condition for capital per effective worker."""
    initial_capital = pwt_data.major_xs(ctry)['rkna'][start]
    initial_labor = pwt_data.major_xs(ctry)['emp'][start]
    initial_output = pwt_data.major_xs(ctry)['rgdpna'][start]
    initial_technology = _technology(initial_capital, initial_labor, 
                                     initial_output, *params)

    return initial_capital / (initial_technology * initial_labor)

def _predicted_labor_share(capital, g, n, s, delta, rho, omega):
    """Model predicted share of income going to labor."""
    if abs(rho) <= 1e-3:
        labor_share = omega
    else:
        labor_share = (1 - omega) / (omega * capital**rho + (1 - omega))

    return labor_share

def _residual(capital, labor_share, g, n, s, delta, rho, omega):
    """Difference between actual and model predicted labor share."""
    actual_labor_share = labor_share
    predicted_labor_share = _predicted_labor_share(capital, g, n, s, delta, rho, omega)
    return actual_labor_share - predicted_labor_share

def _individual_log_likelihood(capital, labor_share, g, n, s, delta, rho, sigma, omega):
    """Individual model log likelihood."""
    # residual is assumed to be drawn from Gaussian with mean zero!
    rv = stats.norm(0, sigma)

    # compute the individual log-likelihood
    residual = _residual(capital, labor_share, g, n, s, delta, rho, omega)
    individual_likelihood = rv.pdf(residual)
    return np.log(individual_likelihood)

def objective(params, ctry, start, end):
    """Total negative log-likelihood for the model."""
    # get relevant data
    labor_share = pwt_data.major_xs(ctry)['labsh'][start:end]

    # solve for the time path of capital
    k0 = _initial_condition(ctry, params, start)

    # compute the total log-likelihood
    total_ll = np.sum(_individual_log_likelihood(k0, labor_share, *params))
    return -total_ll


if __name__ == '__main__':
    
    # ordering is g, n, s, delta, rho, sigma, omega
    test_params = np.array([0.02, 0.02, 0.15, 0.04, 0.0, 0.1, 0.33])

    ctry = 'USA'
    N = pwt_data.major_xs(ctry)['labsh'].size
    test_capital = np.ones(N)

    #print individual_log_likelihood(test_capital, ctry, *test_params)
    print objective(test_params, 'USA', '1950-01-01', '1950-01-01')

    result = optimize.minimize(objective,
                               x0=test_params,
                               args=('USA', '1950-01-01', '1950-01-01'),
                               method='Nelder-Mead',
                               )