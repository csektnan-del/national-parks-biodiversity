# Assessing Biodiversity Risk and Missing Conservation Data in National Parks
This project analyzes biodiversity and conservation risk across multiple U.S. national parks. The goal is to understand:
*  How conservation risk varies across species
*  Whether missing conservation data reflects low risk or incomplete classification
*  Which biological categories (e.g., mammals, fish, plants) face the greatest conservation pressure

## Data Preparation

*  Built a reusable, analysis-ready dataset from raw biodiversity records
*  Cleaned datasets are saved for reproducibility and downstream analysis

*Key steps:*
*  Filled missing conservation statuses as “Not Evaluated” for further investigation
*  For species with inconsistent conservation classifications (e.g., records with both Endangered and In Recovery for the same species), the highest-risk status was assigned to avoid underestimating conservation concern and to standardize labeling
*  For species with multiple observation records within the same park, observation counts were averaged to avoid double counting the same observed organism
*  Duplicate species entries were consolidated to ensure one record per species

## Are “Not Evaluated” species actually low-risk?
Over 95% of species lacked conservation classification.

*Findings:*
*  These species have higher average observation counts than protected species
*  They show minimal to no overlap with Endangered/Threatened groups
*  There is partial overlap with “Species of Concern” in edge cases

**Conclusion:** Most “Not Evaluated” species are likely lower-risk, but a subset may be under-classified.

## Are Certain Parks at Greater Risk for Biodiversity Loss?

Across the four parks in the dataset, is there variance in the number or ratio of protected species?

**Conclusion: The four parks studied show similar risk metrics, with similar counts of protected species, as well as ratio of protected to total species.**

<img width="640" height="480" alt="protected_species_by_park" src="https://github.com/user-attachments/assets/9105a993-6a40-48ec-93fd-b1e7c4187a50" />


<img width="640" height="480" alt="protected_ratio_by_park" src="https://github.com/user-attachments/assets/427b84ca-1e4a-439a-b4be-d8c82309d068" />



## Do Protection Levels Vary by Category?
Are mammals, fish, vascular plants, etc., more likely to be protected than other categories?

## Vascular plants are by far the most observed species in the data
<img width="640" height="480" alt="category_total_species" src="https://github.com/user-attachments/assets/1aeded87-169d-4e71-8176-f09375f37a15" />


## Fish, mammals, and amphibians contain the greatest ratios of protected species
<img width="640" height="480" alt="risk_by_category" src="https://github.com/user-attachments/assets/472edab9-ab60-4679-80c5-cc49fe296da5" />


## While there is a higher ratio of protected fish than protected mammals, they share a similar average risk score.
<img width="640" height="480" alt="category_avg_risk" src="https://github.com/user-attachments/assets/68d0ca89-e62c-4fd5-af69-716db20abbd0" />


## Limitations
*  The vast majority of observations are of vascular plants, making summary data and analysis among other categories more susceptible to outliers
*  Data comes from only four national parks

## Steps for Further Research
*  Incorporating external ecological data (e.g., habitat, climate)
*  Expanding analysis to additional geographic regions

## Tools Used
*  Python (Pandas, Matplotlib)
*  Data cleaning
*  Exploratory data analysis
