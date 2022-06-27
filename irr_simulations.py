# SET ENVIRONMENT VARIABLE `DEVELOPMENT=1` FOR THE PROGRAMME TO WORK!
import multiprocessing as mp
from datetime import datetime
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


def create_initial_irr_schedule(start_date: datetime, end_date: datetime, max_irr: int, irrs_per_month: int = 4):
    """
        Create randomized starting schedule based on irrigating a maximum of twice a week
    """
    month_diff = int(round((end_date - start_date).days / (365 / 12)))

    # Create list of all watering dates in simulation period and random irrigation depths (mm)
    irr_days = pd.date_range(start_date, end_date, periods=month_diff * irrs_per_month)

    # TODO: add bounds such that watering will not be less than 1L per m2
    x0 = np.random.dirichlet(np.ones(len(irr_days)), size=1)[0] * max_irr

    schedule = pd.DataFrame({
        'Date': irr_days,
        'Depth': x0
    })

    return schedule


def objective(x: np.ndarray, schedule: pd.DataFrame, start_date: datetime, end_date: datetime, crop: str, soil: str,
              max_irr_season: int, evaluate: bool = False, verbose: bool = False):
    schedule.Depth = x.astype(int)  # Update the initial/start irrigation schedule with the model optimization step

    irrigate_schedule = IrrigationManagement(irrigation_method=3, Schedule=schedule, MaxIrrSeason=max_irr_season)

    # TODO: define crop stage (emergence, anthesis, max rooting depth, canopy senescence, maturity)
    model = AquaCropModel(
        sim_start_time=start_date.strftime('%Y/%m/%d'),
        sim_end_time=end_date.strftime('%Y/%m/%d'),
        weather_df=prepare_weather(weather_file_path),
        soil=Soil(soil_type=soil),
        crop=Crop(crop, planting_date=start_date.strftime('%m/%d')),
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
        return yield_, total_irr, results['Harvest Date (YYYY/MM/DD)'].values[-1]
    else:
        return -yield_  # Invert in order to maximize the yield


def optimize(start_date: datetime, end_date: datetime, crop: str, soil: str,
             max_irr_season: int, num_searches: int = 1):
    schedules = []
    yields = []
    for i in range(num_searches):
        irrigation_schedule = create_initial_irr_schedule(start_date, end_date, max_irr_season)
        schedules.append(irrigation_schedule)

        yld = objective(irrigation_schedule.Depth.values, irrigation_schedule,
                        start_date, end_date, crop, soil, max_irr_season)
        yields.append(yld)

    # Save best schedule
    solution = schedules[np.argmin(yields)]
    return solution


def find_best_schedule(start: str, end: str, crop: str, soil: str = 'SandyLoam', field_size: int = 1,
                       max_irr_liters: int = 500, verbose: bool = False) -> (pd.DataFrame, str):
    """
        Find best watering schedule for a crop over a given season

        :param start: start date of planting (yyyy/mm/dd)
        :param end: approx. end date of simulation (yyyy/mm/dd)
        :param crop: crop type growing
        :param field_size: size of field in square meters
        :param soil: predefined soil type
        :param max_irr_liters: maximum watering available over season in liters
        :param verbose: draw plots if true
        :returns: Tuple consisting of
            DataFrame containing scheduled watering dates and watering amounts in liters,
            Harvest date (str)
    """
    t0 = time()
    start_date = dateutil.parser.parse(start)
    end_date = dateutil.parser.parse(end)

    max_irr_mm = max_irr_liters / field_size
    max_irrs = np.linspace(0, min(500, max_irr_mm), max(8, mp.cpu_count()), dtype=int)

    # Run objective function optimization for several max irrigation usages
    with mp.Pool(mp.cpu_count()) as pool:
        results = pool.starmap(optimize,
                               [(start_date, end_date, crop, soil, max_irr_season) for max_irr_season in max_irrs])

    print(f"Done. Time taken: {time() - t0}")

    yld_list = []
    total_irr_list = []
    harvest_list = []
    for schedule, max_irr_season in zip(results, max_irrs):
        yld, tirr, harvest_date = objective(schedule.Depth.values, schedule, start_date, end_date, crop, soil,
                                            max_irr_season, evaluate=True, verbose=True)
        yld_list.append(yld)
        total_irr_list.append(max_irr_season)
        harvest_list.append(max_irr_season)

    if verbose:
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

    score_list = np.array(total_irr_list) / (np.array(yld_list) ** 2)
    # argmin but score cannot be 0
    i = np.unravel_index(np.where(score_list!=0, score_list, score_list.max()+1).argmin(), score_list.shape)[0]
    opt_solution = results[i].copy()

    # Convert raining in mm back to liters over the whole field
    opt_solution['Liters'] = opt_solution.Depth * field_size
    opt_solution.set_index('Date', inplace=True)
    opt_solution.index = opt_solution.index.strftime('%Y/%m/%d')

    # Only return the scheduled days where watering is required
    return opt_solution[opt_solution.Liters > 0], harvest_list[i]


if __name__ == "__main__":
    # Run the simulation for a year (assuming crop can be harvested within one year, otherwise it should run longer)
    SIM_START = "1982/05/01"
    SIM_END = "1983/06/01"
    CROP = 'Maize'

    find_best_schedule(SIM_START, SIM_END, CROP, verbose=True)
