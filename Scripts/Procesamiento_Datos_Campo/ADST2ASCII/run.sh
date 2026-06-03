#!/bin/bash

#Define the base directory
# MdSd433DataReconstruction SdInfillDataReconstruction SdDataReconstruction
base="MdSd433DataReconstruction"

# Define the years, months, subset modes and min lgE
#2018 2019 2020 2021 2022 2023 2024 2025
years=(2025)

#01 02 03 04 05 06 07 08 09 10 11 12
months=(01 02 03 04 05 06 07 08 09 10 11 12)

#"PhaseI" "PhaseII" "PhaseIISPMT" "PhaseIIFreeBeta" "PhaseIIFreeBeta2" "PhaseIISPMTFreeBeta" "PhaseIISPMTFreeBeta2" "PhaseIISPMTFreeBeta3" "PhaseIISPMTPhaseIIBeta" "PhaseIISPMTPhaseIIBeta2"
subsets=("PhaseIISPMTPhaseIIBeta")

#Only export T5 events
onlyT5=1

# Only export energetic events
minLgE=0
minLgSref=0

#Only export events with free beta
onlyFreeBeta=0

# Active to refresh all months, not only those with newer events
forceRefresh=true

# Define the XML file name and the C++ application command
xml_file="Config.xml.in"
cpp_app="make run"

# Function to update the XML file
update_xml() {
    year=$1
    month=$2
    subset=$3

    cat > $xml_file <<EOL
<ADSTReader xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

    <!-- Base directory -->
    <base> $base </base>

    <!-- Target month -->
    <year>  $year </year>
    <month> $month </month>

    <!-- Subset -->
    <subset> $subset </subset>

    <!-- Export only T5 events -->
    <onlyT5> $onlyT5 </onlyT5>

    <!-- Export only events above an energy -->
    <minLgE> $minLgE </minLgE>

    <!-- Export only events above a shower size -->
    <minLgSref> $minLgSref </minLgSref>

    <!-- Export only events with free beta -->
    <onlyFreeBeta> $onlyFreeBeta </onlyFreeBeta>

</ADSTReader>
EOL
}

# Loop through each combination and run the C++ application
for year in "${years[@]}"; do
    for month in "${months[@]}"; do
        for subset in "${subsets[@]}"; do

            input_dir="/data5/ngonzale/${base}/Outputs/${year}/${month}"

            # Adjust output path based on base directory
            if [[ "$base" == "SdDataReconstruction" ]]; then
                output_file="./Outputs/1500/${subset}_${year}_${month}"
            elif [[ "$base" == "SdInfillDataReconstruction" ]]; then
                output_file="./Outputs/750/${subset}_${year}_${month}"
            else
                output_file="./Outputs/${subset}_${year}_${month}"
            fi

            if [[ -f "$output_file" ]]; then
              output_mod_time=$(stat -c %Y "$output_file")
              output_mod_date=$(stat -c %y "$output_file")
            else
              output_mod_time=0
              output_mod_date="N/A"
            fi

            input_newer=false
            newest_input_mod_time=0
            newest_input_mod_date="N/A"

            for day in $(seq -w 01 31); do
              input_file="${input_dir}/ADST_${subset}_${year}_${month}_${day}.root"
              if [[ -f "$input_file" ]]; then
                input_mod_time=$(stat -c %Y "$input_file")
                if [[ $input_mod_time -gt $output_mod_time ]]; then
                  input_newer=true
                fi
                if [[ $input_mod_time -gt $newest_input_mod_time ]]; then
                  newest_input_mod_time=$input_mod_time
                  newest_input_mod_date=$(stat -c %y "$input_file")
               fi
              fi
            done

            if [[ $forceRefresh == true ]]; then
                input_newer=true;
            fi

            if [[ $input_newer == true || ! -f "$output_file" ]]; then
              echo "Running for Year: $year, Month: $month, Subset: $subset"
              update_xml $year $month $subset
              $cpp_app
            else
              echo "Skipping Year: $year, Month: $month, Subset: $subset - Output is up to date"
              echo "Output modification date: $output_mod_date"
              echo "Newest input modification date: $newest_input_mod_date"
            fi
        done
    done
done

echo "All runs completed."

