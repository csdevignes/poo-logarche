# poo-logarche
## Context
Final Project POO-Python. Performed for the course of Azim Roussanaly,
IDMC, Université de Lorraine, year 2023-2024.

## Objective
This program aims to :
* extract information from moodle log of the website
Arche, which is the learning platform for IDMC students
* using machine learning, predict the grades of students from their logs

## Organisation
Workflow followed for this problem was :
1. Loading and preprocessing of source .csv files
([logs](/data/logs_anonymes.csv)) and ([grades](data/notes_anonymes.csv))
2. Extraction of features (based on preliminar moodle log observation),
which are saved in the [feature](feature/) folder
3. Merge of features and grades together
4. Exploratory data analysis:
    * Replacement of null values by 0
    * Distribution analysis
    * Filtering out outliers
    * Correlation analysis
5. Optimization of machine learning model: multiple linear regression.
Step backward feature selection.
6. Cross-validation of selected models, with plotting of the metrics.

> Depending on how satisfying the model is, iterations can be made by returning
> to step 2. This project number of iterations: 2.

## Machine learning models and metrics
### Multiple linear regression
Packages from statsmodels and scikit-learn were used for multiple regression.
The following metrics were taken in account for variable selection.
* p-values of each feature
* AIC with/without the feature
* R² with/without the feature
* Mean squared error (MSE) with/without the feature

For cross-validation of the models, only R² and MSE were taken in account.

## TODO
* Implement classification models using created categories "success" and
"mention"
* Implement an interactive interface in the [main](logarche.py)
* Make statistics with the metrics obtained from cross-validation
* Add external dependencies