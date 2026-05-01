#Import neded packages
import pandas as pd
import matplotlib.pyplot as plt

#Load the data
from pathlib import Path
file_path = Path(__file__).parent / "observations.csv"
obs = pd.read_csv(file_path)
file_path = Path(__file__).parent / "species_info.csv"
info = pd.read_csv(file_path)

#Create file to save charts
images_dir = Path(__file__).parent / "images"
images_dir.mkdir(exist_ok=True)

cleaned_data_dir = Path(__file__).parent / "cleaned_data"
cleaned_data_dir.mkdir(exist_ok=True)

#DATA CLEANING
#Are the species with nan for conservation status not endangered, or is that data missing?
#Current categories are 'Species of Concern' 'Endangered' 'Threatened' 'In Recovery'
#For now, assign blanks as 'Not Evaluated' for review later
info['conservation_status']=info['conservation_status'].fillna('Not Evaluated')
#Check all enteries are filled now
#print(info['conservation_status'].isna().sum())

#Simplify common name column
info_clean = info.copy()
info_clean['primary_common_name'] = (
    info_clean['common_names']
    .str.split(',')
    .str[0]
    .str.strip())

#Before removing scientific name duplicates, check there are no differences in endangered status within the same scientific name entry
#print(info_clean.groupby('scientific_name')['conservation_status'].nunique().value_counts())
#Identify conflicting records
conflicting_species = (
    info_clean
    .groupby('scientific_name')['conservation_status']
    .nunique()
    .loc[lambda x: x > 1])
#print(conflicting_species)
#print(info_clean[info_clean['scientific_name'].isin(conflicting_species.index)])

#Consolidate conflicting records based on most highest threat level recorded for that species
info_clean = info_clean[
    ~(
        (info_clean['scientific_name'] == 'Oncorhynchus mykiss') &
        (info_clean['conservation_status'] == 'Not Evaluated'))]
info_clean = info_clean[
    ~(
        (info_clean['scientific_name'] == 'Canis lupus') &
        (info_clean['conservation_status'] == 'In Recovery')
    )]
#Check lower level threat rows where removed for conflicted records
#print(info_clean[info_clean['scientific_name'].isin(['Canis lupus', 'Oncorhynchus mykiss'])])
#Check no conflicting records remain
#print(info_clean.groupby('scientific_name')['conservation_status'].nunique().value_counts())
#Now, any duplicates fully match across all fields, so remove them
info_clean = info_clean.drop_duplicates(subset=['scientific_name'])
#Check no duplicates remain
#print(info_clean['scientific_name'].value_counts().max())

# Check for duplicate species observations within the same park
obs_duplicates = (
    obs
    .groupby(['scientific_name', 'park_name'])
    .size()
    .reset_index(name='row_count')
    .query('row_count > 1'))
#Review the duplicates
duplicate_obs_rows = obs.merge(
    obs_duplicates[['scientific_name', 'park_name']],
    on=['scientific_name', 'park_name'],
    how='inner')
#print(duplicate_obs_rows)
#print(obs_duplicates.head())
#print(len(obs_duplicates))

#Consolidate duplicate species/park rows. Use average to avoid double counting the same animal/plant/etc.
obs_clean = (
    obs
    .groupby(['scientific_name', 'park_name'], as_index=False)
    .agg({'observations': 'mean'}))
obs_clean['observations'] = obs_clean['observations'].round(0).astype(int)
#Check the consolidation was correct
#print(obs_clean.groupby(['scientific_name', 'park_name']).size().max())

#Final checks: all data filled, labels clean, etc.
#print(info_clean['category'].unique())
#print(info_clean['conservation_status'].unique())
#print(obs_clean['observations'].describe())
#print(info_clean.isna().sum())
#print(obs_clean.isna().sum())

#SAVE AND MERGE CLEANED DATA SETS
#Save cleaned
info_clean.to_csv(
    Path(__file__).parent / "cleaned data" / "info_clean.csv",
    index=False)
obs_clean.to_csv(
    Path(__file__).parent / "cleaned data" / "obs_clean.csv",
    index=False)
#Merge
merged = obs_clean.merge(
    info_clean,
    on='scientific_name',
    how='left')
#Check
#print(merged.columns)
#print(merged.shape)
#print(merged.isna().sum())
#print(len(obs_clean))
#print(len(merged))
#Save merged file
merged.to_csv(Path(__file__).parent / "cleaned data" / "cleaned_biodiversity_data.csv", index=False)

#Many of the species didn't have conservation status--does that mean they are not at risk, or is this missing data?
#print(merged['conservation_status'].value_counts(normalize=True))
#Over 95% of the species are Not Evaluated. Investigate their characteristics, compared to those that are labeled with a concern level
status_obs = (
    merged
    .groupby('conservation_status')
    .agg(
        avg_observations=('observations', 'mean'),
        median_observations=('observations', 'median'),
        species_count=('scientific_name', 'nunique')
    )
    .reset_index())
#print(status_obs)
#Observation values for Not Evaluated are the highest of any group, indicating they are not, on average, at risk.
#Investigate cases where Not Evaluated observation counts are close to means of lableed species
#Histogram
ne_obs = merged[
    merged['conservation_status'] == 'Not Evaluated'
]['observations']
plt.figure()
plt.hist(ne_obs, bins=50)
plt.title('Distribution of Not Evaluated Species')
plt.xlabel('Observations')
plt.ylabel('Count')
plt.savefig(images_dir / "Occurances of Not Evalueted Species.png")
#plt.show()
plt.clf()

#Aggregate observations to the species level across parks
species_obs = (
    merged
    .groupby('scientific_name')
    .agg(
        avg_obs=('observations', 'mean'),
        total_obs=('observations', 'sum'),
        park_count=('park_name', 'nunique'),
        conservation_status=('conservation_status', 'first')
    )
    .reset_index())
#Understand overlap between categories
#print(species_obs.groupby('conservation_status')['avg_obs'].quantile([0.1, 0.25, 0.5, 0.75, 0.9]))
#Only the lowest observations of the Not Evaluated category overlap with the highest among Species of Concern, therefore, leave categorization as is

#ANALYZE CONSERVATION RISK BY PARK
#Assign scores per conservation level
risk_scores = {
    'Endangered': 3,
    'Threatened': 2,
    'Species Of Concern': 1,
    'Not Evaluated': 0}
#Add to merged dataset
merged['risk_score'] = merged['conservation_status'].map(risk_scores)
#Define protected groups
merged['is_protected'] = merged['conservation_status'].isin([
    'Endangered', 'Threatened', 'Species Of Concern', 'In Recovery'])
#Aggregate at the park level
park_summary = (
    merged
    .groupby('park_name')
    .agg(
        total_species=('scientific_name', 'nunique'),
        total_observations=('observations', 'sum'),
        protected_species=('is_protected', 'sum'),
        total_risk_score=('risk_score', 'sum'),
        avg_risk_score=('risk_score', 'mean')
    )
    .reset_index())
park_summary['protected_ratio'] = (
    park_summary['protected_species'] / park_summary['total_species'])

#Create a charting function
def plot_bar(df, x, y, title, ylabel, filename):
    plt.figure()
    plt.bar(df[x], df[y])
    plt.xticks(rotation=45)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(images_dir / filename)
    #plt.show()
    plt.clf()
#Plot total species
plot_bar(park_summary.sort_values('total_species', ascending=False), 
         'park_name', 'total_species',
         'Total Species by Park', 'Species Count',
         'total_species_by_park.png')
#Plot protected species
plot_bar(park_summary.sort_values('protected_species', ascending=False), 
         'park_name', 'protected_species',
         'Protected Species by Park', 'Count',
         'protected_species_by_park.png')
#Plot protected ratio
plot_bar(park_summary.sort_values('protected_ratio', ascending=False), 
         'park_name', 'protected_ratio',
         'Protected Species Ratio by Park', 'Ratio',
         'protected_ratio_by_park.png')
#Plot total risk score
plot_bar(park_summary.sort_values('total_risk_score', ascending=False), 
         'park_name', 'total_risk_score',
         'Total Risk Score by Park', 'Risk Score',
         'total_risk_score_by_park.png')
#Plot avg risk score
plot_bar(park_summary.sort_values('avg_risk_score', ascending=False), 
         'park_name', 'avg_risk_score',
         'Average Risk Score by Park', 'Avg Risk',
         'avg_risk_score_by_park.png')

#Conservation risk is largely even across parks, pivot to looking at risk by class
category_risk = (
    merged
    .groupby('category')
    .agg(
        total_species=('scientific_name', 'nunique'),
        protected_species=('is_protected', 'sum'),
        total_risk_score=('risk_score', 'sum'),
        avg_risk_score=('risk_score', 'mean')
    )
    .reset_index())
category_risk['protected_ratio'] = (
    category_risk['protected_species'] / category_risk['total_species'])
#print(category_risk.sort_values('protected_ratio', ascending=False))
#Species by category counts
plot_bar(
    category_risk.sort_values('total_species', ascending=False),
    'category',
    'total_species',
    'Total Species by Category',
    'Species Count',
    'category_total_species.png')
#Protected species by category
plot_bar(
    category_risk.sort_values('protected_species', ascending=False),
    'category',
    'protected_species',
    'Protected Species by Category',
    'Count',
    'category_protected_species.png'
)
#Protected ratio by category
plot_bar(
    category_risk.sort_values('protected_ratio', ascending=False),
    'category',
    'protected_ratio',
    'Risk by Category (Protected Ratio)',
    'Ratio',
    'risk_by_category.png')
#Total risk by category
plot_bar(
    category_risk.sort_values('total_risk_score', ascending=False),
    'category',
    'total_risk_score',
    'Total Risk Score by Category',
    'Risk Score',
    'category_total_risk.png'
)
#Average risk by category
plot_bar(
    category_risk.sort_values('avg_risk_score', ascending=False),
    'category',
    'avg_risk_score',
    'Average Risk Score by Category',
    'Avg Risk',
    'category_avg_risk.png'
)