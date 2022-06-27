# SET ENVIRONMENT VARIABLE `DEVELOPMENT=1` FOR THE PROGRAMME TO WORK!
import multiprocessing as mp
# time library so we can check the speed up
from time import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement
from aquacrop.utils import prepare_weather, get_filepath
from scipy.optimize import fmin
import dateutil.parser

# TODO: use actual climate from Tamale
path = get_filepath('champion_climate.txt')
wdf = prepare_weather(path)


def create_initial_irr_schedule(sim_start, sim_end, max_irr, irrs_per_month=2):
    """
        Create randomized starting schedule based on irrigating a maximum of twice a week
    """
    start_date = dateutil.parser.parse(sim_start)
    end_date = dateutil.parser.parse(sim_end)

    month_diff = int(round((end_date - start_date).days / (365 / 12)))

    # Create list of all watering dates in simulation period and random irrigation depths (mm)
    irr_days = pd.date_range(sim_start, sim_end, periods=month_diff * irrs_per_month)
    x0 = np.random.dirichlet(np.ones(len(irr_days)), size=1)[0] * max_irr

    schedule = pd.DataFrame({
        'Date': irr_days,
        'Depth': x0
    })

    return schedule


def run_model(schedule, max_irr_season, start_date, end_date):
    """
        Function to run model and return results for given set of soil moisture targets
    """
    maize = Crop('Maize', planting_date='05/01')  # define crop
    loam = Soil('ClayLoam')  # define soil
    init_wc = InitialWaterContent(wc_type='Pct', value=[0])  # define initial soil water conditions

    # TODO: use `AppEff` to specify efficiency of watering based on irrigation method
    # SMT = Soil Moisture Targets
    # irrmngt = IrrigationManagement(irrigation_method=1, SMT=smts, MaxIrrSeason=max_irr_season)
    irrmngt = IrrigationManagement(irrigation_method=3, Schedule=schedule, MaxIrrSeason=max_irr_season)

    # create and run model
    model = AquaCropModel(
        sim_start_time=start_date,
        sim_end_time=end_date,
        weather_df=wdf,
        soil=loam,
        crop=maize,
        irrigation_management=irrmngt,
        initial_water_content=init_wc)

    model.run_model(till_termination=True)
    return model.get_simulation_results()


def objective(x0, schedule, max_irr_season, start_date, end_date, test=False):
    """
        Function to run model and calculate reward (yield) for given set of soil moisture targets
    """
    # run model
    schedule['Depth'] = x0
    out = run_model(schedule, max_irr_season, start_date, end_date)

    # Get yields and total irrigation
    yld = out['Yield (tonne/ha)'].mean()
    tirr = out['Seasonal irrigation (mm)'].mean()

    reward = yld

    # return either the negative reward (for the optimization)
    # or the yield and total irrigation (for analysis)
    if test:
        return yld, tirr, reward
    else:
        return -reward


# def get_starting_point(num_smts, max_irr_season, num_searches):
#     """
#     find good starting threshold(s) for optimization
#     """
#
#     # get random SMT's
#     x0list = np.random.rand(num_searches, num_smts) * 100
#     rlist = []
#     # evaluate random SMT's
#     for xtest in x0list:
#         r = objective(xtest, max_irr_season, )
#         rlist.append(r)
#
#     # save best SMT
#     x0 = x0list[np.argmin(rlist)]
#
#     return x0


def optimize(max_irr_season):
    """Optimize thresholds to be profit maximising"""
    # x0 = get_starting_point(4, max_irr_season, num_searches)  # Get starting schedule optimization strategy
    start_date = '2016/05/01'
    end_date = '2017/05/01'

    schedule = create_initial_irr_schedule(start_date, end_date, max_irr_season)
    x0 = schedule.Depth.values

    # Run optimization on given schedule
    res = fmin(objective, x0, disp=0, args=(schedule, max_irr_season, start_date, end_date,))

    opt_schedule = res.squeeze()

    yld, tirr, _ = objective(opt_schedule, max_irr_season, start_date, end_date, True)  # Evaluate optimal strategy

    print(f"finished max_irr = {max_irr_season} at {round(time() - start)} seconds")
    return yld, tirr, opt_schedule


if __name__ == "__main__":
    start = time()

    # Run objective function optimization for several max irrigation usages
    with mp.Pool(1) as p:
        results = p.map(optimize, list(range(0, 500, 100)))

    opt_smts = []
    yld_list = []
    tirr_list = []

    for i in range(len(results)):
        yld_list.append(results[i][0])
        tirr_list.append(results[i][1])
        opt_smts.append(results[i][2])

    fig, ax = plt.subplots(1, 1, figsize=(13, 8))

    # plot results
    ax.scatter(tirr_list, yld_list)
    ax.plot(tirr_list, yld_list)

    # labels
    ax.set_xlabel('Total Irrigation (ha-mm)', fontsize=18)
    ax.set_ylabel('Yield (tonne/ha)', fontsize=18)
    ax.set_xlim([-20, 600])
    ax.set_ylim([2, 15.5])

    # annotate with optimal thresholds
    bbox = dict(boxstyle="round", fc="1")
    offset = [15, 15, 15, 15, 15, -125, -100, -5, 10, 10]
    yoffset = [0, -5, -10, -15, -15, 0, 10, 15, -20, 10]
    for i, smt in enumerate(opt_smts):
        smt = smt.clip(0, 100)
        ax.annotate('(%.0f, %.0f, %.0f, %.0f)' % (smt[0], smt[1], smt[2], smt[3]),
                    (tirr_list[i], yld_list[i]), xytext=(offset[i], yoffset[i]), textcoords='offset points',
                    bbox=bbox, fontsize=12)

    plt.show()
