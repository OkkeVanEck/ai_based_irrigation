# SET ENVIRONMENT VARIABLE `DEVELOPMENT=1` FOR THE PROGRAMME TO WORK!

import numpy as np
import pandas as pd
from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent, IrrigationManagement
from aquacrop.utils import prepare_weather, get_filepath
from scipy.optimize import minimize


# TODO: use actual climate from Tamale
weather_file_path = get_filepath('champion_climate.txt')


# TODO: Use days instead of weeks for the simulation. Days now take to long if done for a whole week
def create_pandas_irrigation_schedule(sim_start, sim_end):
    """This function create an irrigation schedule"""
    all_days = pd.date_range(sim_start, sim_end)  # list of all dates in simulation period

    new_month = True
    dates = []
    # iterate through all simulation days
    for date in all_days:
        # check if new month
        if date.is_month_start:
            new_month = True

        if new_month:
            # check if tuesday (dayofweek=1)
            if date.dayofweek == 1:
                # save date
                dates.append(date)
                new_month = False

    return dates


def objective(x, dates, eps, sign=-1.):
    schedule = pd.DataFrame([dates, x]).T
    schedule.columns = ["Date", "Depth"]

    schedule.iloc[:, 1] /= eps
    schedule['Depth'] = schedule['Depth'].astype('int')

    irrigate_schedule = IrrigationManagement(irrigation_method=3, Schedule=schedule)

    # TODO: define crop stage (emergence, anthesis, max rooting depth, canopy senescence, maturity)
    model_os = AquaCropModel(
        sim_start_time=SIM_START,
        sim_end_time=SIM_END,
        weather_df=prepare_weather(weather_file_path),
        soil=SOIL_TYPE,
        crop=CROP,
        initial_water_content=InitialWaterContent(value=['FC']),
        irrigation_management=irrigate_schedule,
    )

    model_os.run_model(till_termination=True)
    print(f"Total irr: {sum(schedule['Depth'])}; harvest: {sum(model_os.get_simulation_results()['Yield (tonne/ha)'])}")
    return sign*(sum(model_os.get_simulation_results()['Yield (tonne/ha)']))  # Invert in order to maximize the yield


def max_water_constraint(x):
    # Constraints are normalized to (inequality) MAX_WATER_MM - sum(x) >= 0
    return MAX_WATER_MM - sum(x)


# TODO: use actual input from user
SIM_START = "1982/05/01"
SIM_END = "1983/06/01"  # Run the simulation for a year (assuming crop can be harvested within one year, otherwise it should run longer)
SOIL_TYPE = Soil(soil_type='SandyLoam')
CROP = Crop('Maize', planting_date='05/01')


# TODO: use multi-start to run multiple simulations with different starting schedules
for eps in [1e-4, 1e-3, 1e-2, 1e-1]:
    MAX_WATER_MM = 250 * eps

    irrigation_schedule = create_pandas_irrigation_schedule(SIM_START, SIM_END)

    n = len(irrigation_schedule)

    # TODO: create better initialized starting irrigation schedule
    x0 = np.random.dirichlet(np.ones(n), size=1)[0] * MAX_WATER_MM  # Random starting point using max amount of water

    solution = minimize(objective, x0, (irrigation_schedule, eps),
                        method='SLSQP',
                        bounds=[(.0, 1. * MAX_WATER_MM)] * n,  # Amount of water on a single day cannot be lower than 0 or higher than the max
                        constraints=[{'type': 'ineq', 'fun': max_water_constraint}],  # Total amount of water may not exceed max
                        options={'eps': eps, 'disp': True})

    best_irr_schedule = schedule = pd.DataFrame([irrigation_schedule, solution.x]).T
    best_irr_schedule.columns = ["Date", "Irrigation (Liter per hectare)"]
    best_irr_schedule["Irrigation (Liter per hectare)"] /= eps

    print(f"\nBest irrigation schedule (eps {eps}):\n"
          f"{best_irr_schedule.to_string()}\n")

    # TODO: return useful output
