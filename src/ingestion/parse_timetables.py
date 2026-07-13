"""
Parses TransXChange XML timetable files into a single trip-level CSV.
Extracts one row per scheduled vehicle journey (trip), combining
Operator, Service, and VehicleJourney information.

Tool used: Python's built-in xml.etree.ElementTree

Operating days (days_of_week) are looked up at the Service level first;
if a specific VehicleJourney overrides this (common in some operators'
export formats, e.g. Stagecoach), that override takes priority.
"""

import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET

# TransXChange default namespace — required for all tag lookups
NS = {'txc': 'http://www.transxchange.org.uk/'}


def get_days_of_week(profile_elem):
    """Extract day-of-week child tag names from a RegularDayType element."""
    if profile_elem is None:
        return []
    days_elem = profile_elem.find('txc:DaysOfWeek', NS)
    if days_elem is None:
        return []
    return [child.tag.split('}')[-1] for child in days_elem]


def parse_single_file(filepath):
    """Extract trip-level rows from one TransXChange XML file."""
    rows = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # --- Operator info ---
        operator_elem = root.find('.//txc:Operators/txc:Operator', NS)
        operator_name = operator_elem.find('txc:OperatorShortName', NS).text if operator_elem is not None else None
        noc = operator_elem.find('txc:NationalOperatorCode', NS).text if operator_elem is not None else None

        # --- Service info (route/line details) ---
        service_elem = root.find('.//txc:Services/txc:Service', NS)
        service_code = service_elem.find('txc:ServiceCode', NS).text if service_elem is not None else None

        line_elem = service_elem.find('.//txc:Line', NS) if service_elem is not None else None
        line_name = line_elem.find('txc:LineName', NS).text if line_elem is not None else None

        std_service = service_elem.find('txc:StandardService', NS) if service_elem is not None else None
        origin = std_service.find('txc:Origin', NS).text if std_service is not None else None
        destination = std_service.find('txc:Destination', NS).text if std_service is not None else None

        # --- Operating days: Service-level default ---
        service_profile = service_elem.find('.//txc:OperatingProfile/txc:RegularDayType', NS) if service_elem is not None else None
        service_days = get_days_of_week(service_profile)

        start_date_elem = service_elem.find('.//txc:OperatingPeriod/txc:StartDate', NS) if service_elem is not None else None
        operating_start = start_date_elem.text if start_date_elem is not None else None

        # --- Vehicle Journeys (actual trips) ---
        for vj in root.findall('.//txc:VehicleJourneys/txc:VehicleJourney', NS):
            departure_time = vj.find('txc:DepartureTime', NS)
            journey_code_elem = vj.find('.//txc:JourneyCode', NS)

            # Fallback: this specific VehicleJourney may override operating days
            vj_profile = vj.find('.//txc:OperatingProfile/txc:RegularDayType', NS)
            vj_days = get_days_of_week(vj_profile)
            final_days = vj_days if vj_days else service_days

            rows.append({
                'source_file': os.path.basename(filepath),
                'operator_name': operator_name,
                'national_operator_code': noc,
                'service_code': service_code,
                'line_name': line_name,
                'origin': origin,
                'destination': destination,
                'days_of_week': ','.join(final_days),
                'operating_start_date': operating_start,
                'journey_code': journey_code_elem.text if journey_code_elem is not None else None,
                'departure_time': departure_time.text if departure_time is not None else None,
            })

    except ET.ParseError as e:
        print(f"  [ERROR] Failed to parse {filepath}: {e}")
    except AttributeError as e:
        print(f"  [WARNING] Missing expected element in {filepath}: {e}")

    return rows


def parse_all_timetables(base_dir="data/raw/timetables"):
    """Loop through every operator subfolder and every XML file within it."""
    all_rows = []
    operator_folders = ['stagecoach', 'arriva', 'transdev', 'first_bus', 'go_ahead']

    for folder in operator_folders:
        folder_path = os.path.join(base_dir, folder)
        xml_files = glob.glob(os.path.join(folder_path, '**', '*.xml'), recursive=True)
        print(f"{folder}: found {len(xml_files)} XML files")

        for filepath in xml_files:
            rows = parse_single_file(filepath)
            all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    print(f"\nTotal trip rows extracted: {len(df)}")

    missing_days = df['days_of_week'].isin(['', None]).sum() if len(df) else 0
    print(f"Rows still missing days_of_week after fallback: {missing_days}")

    return df


if __name__ == "__main__":
    df = parse_all_timetables()
    output_path = "data/interim/timetables_parsed.csv"
    os.makedirs("data/interim", exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")