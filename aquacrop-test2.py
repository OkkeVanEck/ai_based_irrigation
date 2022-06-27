# SET ENVIRONMENT VARIABLE `DEVELOPMENT=1` FOR THE PROGRAMME TO WORK!
import multiprocessing as mp

import dateutil.parser
import numpy as np
import pandas as pd
from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement
from aquacrop.utils import prepare_weather, get_filepath
from scipy.optimize import fmin_tnc, minimize

# TODO: use actual climate from Tamale
weather_file_path = get_filepath('champion_climate.txt')


# TODO: Use days instead of weeks for the simulation. Days now take to long if done for a whole week
def create_initial_irr_schedule(sim_start, sim_end, max_irr, irrs_per_month=1):
    """
        Create randomized starting schedule based on irrigating a maximum of twice a week
    """
    start_date = dateutil.parser.parse(sim_start)
    end_date = dateutil.parser.parse(sim_end)

    month_diff = int(round((end_date - start_date).days / (365 / 12)))

    # Create list of all watering dates in simulation period and random irrigation depths (mm)
    irr_days = pd.date_range(sim_start, sim_end, periods=month_diff * irrs_per_month)
    x0 = np.random.dirichlet(np.ones(len(irr_days)), size=1)[0] * 50

    schedule = pd.DataFrame({
        'Date': irr_days,
        'Depth': x0
    })

    return schedule


def objective(x, schedule, start_date, end_date, max_irr_season):
    schedule.Depth = x / EPS  # Update the initial/start irrigation schedule with the model optimization step

    irrigate_schedule = IrrigationManagement(irrigation_method=3, Schedule=schedule, MaxIrrSeason=max_irr_season)

    # TODO: define crop stage (emergence, anthesis, max rooting depth, canopy senescence, maturity)
    model = AquaCropModel(
        sim_start_time=start_date,
        sim_end_time=end_date,
        weather_df=prepare_weather(weather_file_path),
        soil=SOIL_TYPE,
        crop=CROP,
        initial_water_content=InitialWaterContent(value=['FC']),
        irrigation_management=irrigate_schedule,
    )

    model.run_model(till_termination=True)
    results = model.get_simulation_results()

    yield_ = results['Yield (tonne/ha)'].mean()
    total_irr = schedule.Depth.sum()

    print(f"Total irr: {total_irr}; harvest: {yield_}")
    return -yield_  # Invert in order to maximize the yield


def optimize(max_irr_season):
    print(max_irr_season)
    max_irr_season_scaled = max_irr_season * EPS
    irrigation_schedule = create_initial_irr_schedule(SIM_START, SIM_END, max_irr_season * EPS)

    solution = minimize(objective, irrigation_schedule.Depth.values,
                        args=(irrigation_schedule, SIM_START, SIM_END, max_irr_season),
                        method='SLSQP',
                        bounds=[(.0, 1. * max_irr_season_scaled)] * len(irrigation_schedule.Date),
                        constraints=({'type': 'ineq',
                                      'fun': max_water_constraint,
                                      'args': (max_irr_season_scaled,)}),  # Total amount of water may not exceed max
                        options={'eps': EPS, 'disp': True})

    # solution = fmin_tnc(objective, irrigation_schedule.Depth.values,
    #                     args=(irrigation_schedule, SIM_START, SIM_END, max_irr_season),
    #                     bounds=[(.0, 1. * max_irr_season_scaled)] * len(irrigation_schedule.Date),
    #                     fprime=None,
    #                     approx_grad=True, disp=1)

    return solution


def max_water_constraint(x, max_irr_season):
    # Constraints are normalized to (inequality) MAX_WATER_MM - sum(x) >= 0
    return max_irr_season - sum(x)


# TODO: use actual input from user
SIM_START = "1982/05/01"
SIM_END = "1983/06/01"  # Run the simulation for a year (assuming crop can be harvested within one year, otherwise it should run longer)
SOIL_TYPE = Soil(soil_type='SandyLoam')
CROP = Crop('Maize', planting_date='05/01')
EPS = 1e-1

if __name__ == "__main__":
    # Run objective function optimization for several max irrigation usages
    with mp.Pool(1) as p:
        # results = p.map(optimize, list(range(0, 500, 100)))
        results = p.map(optimize, [500])

    a = 1

    # best_irr_schedule = schedule = pd.DataFrame([irrigation_schedule, solution.x]).T
    # best_irr_schedule.columns = ["Date", "Irrigation (Liter per hectare)"]
    # best_irr_schedule["Irrigation (Liter per hectare)"] /= eps
    #
    # print(f"\nBest irrigation schedule (eps {eps}):\n"
    #       f"{best_irr_schedule.to_string()}\n")
    #
    # # TODO: return useful output
