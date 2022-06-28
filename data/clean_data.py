#!/usr/bin/env python3
import pandas as pd
import numpy as np
from pathlib import Path
import os


def clean_tutiempo():
    """Cleans the datasets of Tutiempo and stores a cleaned copy."""
    # Create main folder for cleaned Tutiempo data.
    os.makedirs(Path(f"cleaned/tutiempo"), exist_ok=True)

    # Clean all files.
    for root, dirs, files in os.walk(Path("tutiempo")):
        # Create cleaned folder and print debug if files will be cleaned.
        if len(files) > 0:
            print(f"\tCleaning {root[4:]}..")
            os.makedirs(Path(f"cleaned/{root[4:]}"), exist_ok=True)

        # Clean each file in the subfolder and save a cleaned copy.
        for fname in files:
            df_raw = pd.read_csv(Path(f"{root}/{fname}"), index_col="Day")

            # Remove empty rows.
            df_raw = df_raw.replace("", np.nan)
            df_raw = df_raw.dropna(subset=["T"])

            # Store cleaned copy.
            df_raw.to_csv(Path(f"cleaned/{root[4:]}/{fname}"))


if __name__ == "__main__":
    # Create cleaned folder if it does not exist yet.
    os.makedirs(Path(f"cleaned"), exist_ok=True)

    # Clean Tutiempo weather data.
    print("\nProcessing Tutiempo data..")
    clean_tutiempo()
