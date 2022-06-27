# SET ENVIRONMENT VARIABLE `DEVELOPMENT=1` FOR THE PROGRAMME TO WORK!
import multiprocessing as mp
from time import time

import dateutil.parser
import numpy as np
import pandas as pd
from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement
from aquacrop.utils import prepare_weather, get_filepath
from matplotlib import pyplot as plt
from scipy.optimize import fmin_tnc, minimize

# TODO: use actual climate from Tamale
weather_file_path = get_filepath('champion_climate.txt')


# TODO: Use days instead of weeks for the simulation. Days now take to long if done for a whole week
def create_initial_irr_schedule(sim_start, sim_end, max_irr, irrs_per_month=4):
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


def objective(x, schedule, start_date, end_date, max_irr_season, evaluate=False, verbose=False):
    schedule.Depth = x.astype(int)  # Update the initial/start irrigation schedule with the model optimization step

    irrigate_schedule = IrrigationManagement(irrigation_method=3, Schedule=schedule, MaxIrrSeason=max_irr_season)

    # TODO: define crop stage (emergence, anthesis, max rooting depth, canopy senescence, maturity)
    model = AquaCropModel(
        sim_start_time=start_date,
        sim_end_time=end_date,
        weather_df=prepare_weather(weather_file_path),
        soil=SOIL_TYPE,
        crop=CROP,
        initial_water_content=InitialWaterContent(wc_type='Pct', value=[0]),
        irrigation_management=irrigate_schedule,
    )

    model.run_model(till_termination=True)
    results = model.get_simulation_results()

    yield_ = results['Yield (tonne/ha)'].mean()
    # total_irr = schedule.Depth.sum()
    total_irr = results['Seasonal irrigation (mm)'].mean()

    if verbose:
        print(f"Total irr: {total_irr}; harvest: {yield_}")

    if evaluate:
        return yield_, total_irr
    else:
        return -yield_  # Invert in order to maximize the yield


def optimize(max_irr_season, num_searches=100):
    schedules = []
    yields = []
    for i in range(num_searches):
        irrigation_schedule = create_initial_irr_schedule(SIM_START, SIM_END, max_irr_season)
        schedules.append(irrigation_schedule)

        yld = objective(irrigation_schedule.Depth.values, irrigation_schedule, SIM_START, SIM_END, max_irr_season)
        yields.append(yld)

    # Save best schedule
    solution = schedules[np.argmin(yields)]
    return solution


# TODO: use actual input from user
SIM_START = "1982/05/01"
SIM_END = "1983/06/01"  # Run the simulation for a year (assuming crop can be harvested within one year, otherwise it should run longer)
SOIL_TYPE = Soil(soil_type='SandyLoam')
CROP = Crop('Maize', planting_date='05/01')

if __name__ == "__main__":
    start = time()
    max_irrs = np.linspace(0, 500, mp.cpu_count(), dtype=int)

    # Run objective function optimization for several max irrigation usages
    with mp.Pool(mp.cpu_count()) as p:
        results = p.map(optimize, max_irrs)

    print(f"Done. Time taken: {time() - start}")

    yld_list = []
    total_irr_list = []
    for schedule, max_irr_season in zip(results, max_irrs):
        yld, tirr = objective(schedule.Depth.values, schedule, SIM_START, SIM_END, max_irr_season,
                              evaluate=True, verbose=True)
        yld_list.append(yld)
        total_irr_list.append(tirr)

    fig, ax = plt.subplots(1, 1, figsize=(13, 8))

    # plot results
    ax.scatter(total_irr_list, yld_list)
    ax.plot(total_irr_list, yld_list)

    # labels
    ax.set_xlabel('Total Irrigation (ha-mm)', fontsize=18)
    ax.set_ylabel('Yield (tonne/ha)', fontsize=18)
    ax.set_xlim([-20, 600])
    ax.set_ylim([2, 15.5])

    plt.show()

    a = 1

    # best_irr_schedule = schedule = pd.DataFrame([irrigation_schedule, solution.x]).T
    # best_irr_schedule.columns = ["Date", "Irrigation (Liter per hectare)"]
    # best_irr_schedule["Irrigation (Liter per hectare)"] /= eps
    #
    # print(f"\nBest irrigation schedule (eps {eps}):\n"
    #       f"{best_irr_schedule.to_string()}\n")
    #
    # # TODO: return useful output
