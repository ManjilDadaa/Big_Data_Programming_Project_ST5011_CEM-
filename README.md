# Bus Disruption Recovery Time and Severity Prediction

This is my ST5011CEM Big Data Programming Project coursework. The goal of this project is to build a predictive analytics platform that estimates how severe a bus service disruption is likely to be, using real timetable and disruption data published by the UK Bus Open Data Service (BODS). I scoped the project to West Yorkshire, since that region had the highest volume of usable disruption records among the transport authorities publishing to BODS at the time I collected the data.

## Project Overview

The intended user of this system is a transport authority (modelled on WYCA, the West Yorkshire Combined Authority) that wants to understand how disruptions on the bus network are likely to play out once they happen, so that they can prioritise which ones need active intervention.

I ended up building two separate classification tasks rather than one:

1. Predicting whether a scheduled trip will be disrupted at all, using only schedule based features (time of day, day of week, operator). This one is documented as a negative result. The models could not distinguish disrupted trips from normal ones better than chance, and I dug into why that is in the report rather than hiding it.
2. Predicting the severity of a disruption (minor, moderate, severe) once a disruption is already known to be happening, using the disruption's own characteristics (reason, planned status). This one worked reasonably well, with the tuned Random Forest reaching about 69% accuracy and 100% recall on severe cases.

## Tech Stack

- PySpark, for all large scale data transformation, the trip expansion join, and the ML pipeline (MLlib)
- Pandas, matplotlib, seaborn, for smaller scale exploration and the final plotting step
- PostgreSQL (hosted on Supabase), for storing the processed dataset
- SQLAlchemy and python-dotenv, for database access without hardcoding credentials
- Jupyter notebooks, for the whole workflow

## Data Sources

- BODS Data Catalogue, `disruptions_data_catalogue.csv`, filtered to WYCA
- BODS Timetables data, downloaded as TransXChange XML files for the operators serving West Yorkshire (Stagecoach Yorkshire was downloaded but later excluded, since it turned out to be mostly South Yorkshire routes despite the naming)

I scoped the analysis to a three month window, 1 April 2026 to 30 June 2026, since that matched the extended date range strategy suggested in the assignment brief and lined up with when most of the downloaded timetable data was actually valid.

## Setup

1. Clone this repository
2. I used my existing PySpark environment (`sparkenv`) rather than creating a new one, since PySpark was already installed there via `pip install pyspark`. Activate it before running anything:
   ```
   source ~/Desktop/sparkenv/bin/activate
   ```
3. Install the remaining dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root with your own database connection string (I am not including mine, obviously):
   ```
   DATABASE_URL=postgresql://user:password@host:port/dbname
   ```
5. Register the environment as a Jupyter kernel if it is not already:
   ```
   python -m ipykernel install --user --name=sparkenv --display-name="Python (sparkenv)"
   ```
6. Open the notebooks in order, described below.

## Project Structure

```
data/
  raw/            downloaded BODS files, not tracked in git
  interim/        intermediate cleaned/parsed data, not tracked in git
  processed/      final model ready datasets, not tracked in git
notebooks/        the whole pipeline, numbered in the order they should be run
src/
  ingestion/      the TransXChange XML parser
docs/             architecture diagram, database schema dump, sample queries, Spark UI screenshots
outputs/
  figures/        all charts and result tables generated along the way
  models/         (not currently used, reserved for saved model artifacts)
```

## Notebooks, in Order

- `01_data_exploration.ipynb`: first look at the disruptions catalogue and the raw timetable XML, includes the date parsing fix and the three month scoping of disruptions
- `02_data_cleaning.ipynb`: geographic filtering down to West Yorkshire operators, the calendar based trip expansion (broadcast join), and deduplication of the expanded trip instances
- `03_disruption_join.ipynb`: links disruptions to individual trips using a sampling based approach, since BODS does not provide an exact key connecting disruptions to affected services. This is the notebook where I worked out the severity labelling and fixed a couple of timezone and stale kernel state bugs along the way
- `04_feature_engineering.ipynb`: builds the cyclical time features, one hot encodes the categorical columns, and creates the time based train and test split
- `05_modeling.ipynb`: trains and evaluates Logistic Regression, Decision Tree, and Random Forest for the disruption occurrence task, including the class weighting attempt and the CrossValidator run, all of which confirmed the same negative result
- `06_severity_modeling.ipynb`: the second, more successful modeling task, predicting severity among already disrupted trips, using a disruption level train and test split so the same disruption cannot leak across both sets
- `07_database.ipynb`: sets up the PostgreSQL schema on Supabase and loads the processed data in
- `08_eda_visualizations.ipynb`: the exploratory charts, correlation and distribution analysis, and the PySpark SQL query examples

## A Couple of Honest Notes

The disruption occurrence model not working is not a bug, I checked this from several angles (feature leakage, sampling bias in the operator feature, raw probability distributions, and a model independent aggregation check on disruption rate by hour and weekday). All of them point to the same conclusion, which is that schedule based features alone do not carry a usable signal for predicting whether a disruption will happen. I think this is a reasonable finding given the constraints of the data, not a failure of the pipeline.

The `is_disrupted` label itself is not something BODS provides directly. Since the disruptions catalogue does not link disruptions to specific affected services, I built the label by randomly sampling operator and line combinations for each real disruption, calibrated to that disruption's reported number of affected services. This is documented properly in the report, including where it introduced its own problems (an early version of the severity model was accidentally leaking the sampling structure through the operator feature, which I caught by checking feature importances and disruption rates per operator before finalising the model).

## Author

Manjil, Softwarica College of IT and E-Commerce, ST5011CEM