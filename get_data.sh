#!/usr/bin/env bash
# This script collects data from the selected datasets and stores it in the data
# folder.

# Fetch historical weather data from Tamale, Ghana.
fetch_weather() {
    years=("$@")
    declare -a months=("01" "02" "03" "04" "05" "06" "07" "08" "09" "10" "11"
                       "12")
    link_begin="https://en.tutiempo.net/climate"
    link_end="ws-654180.html"

    # Create a folder for weather data.
    mkdir -p data/weather

    # Create a subfolder for every year and store CSV files there.
    for y in "${years[@]}"; do
        mkdir -p "data/weather/$y"

        # If a month has data, download the CSV file.
        for m in "${months[@]}"; do
            # Store HTTP version and response code of month page.
            url="$link_begin/$m-$y/$link_end"
            resp=$(curl -s --head  "$url" | head -n 1)
            read -ra resp <<< "$resp"

            # Continue if page with month does not exists (gives a 404).
            if [ "${resp[1]}" == "404" ]; then
                echo -e "$m-$y:\tNo data available.."
                continue
            fi

            # If page exists, download and store CSV.

        done
    done
}

# Main entry point of the script.
main() {
    # Create data folder, if not exists yet.
    mkdir -p data

    # Fetch historical weather data.
    years=("2022" "2021" "2020")
    years=("2022")
    fetch_weather "${years[@]}"
}

main "$@"
