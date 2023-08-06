# feature_test

This package provides tools to test one feature against all other features in a dataset. It is intended to determine whether a new feature is a good candidate for addition to an established dataset used in a machine learning model. The benefit of this package is that instead of adding a feature to a dataset, running it through a long training and evaluation process, and then interpreting results, the feature can be quickly tested using feature_test; enabling users to quickly discard unuseful features and move forward with potentially impactful ones. This package provides the following tools to aid this determination.

- Correlation analysis
    - Calculate the correlations
    - Identify highly correlated feature
    - Categorize correlation
- Chi-Square tests
    - Calculate the chi-square statistic and p-vlaue
    - Categorize the chi-square result
- Recursive feature elimination (RFE)
    - Rank features by their importance
- Lasso regularization coefficients 
    - Calculate the coefficients of a linear model using Lasso regularization
- Ridge regularization coefficients
    - Calculate the coefficients of a linear model using Ridge Regularization
- Decision tree coefficients
    - Calculate the coefficients for each feature using a decision tree model

* Special thanks to the AREN team for their guidance and Annie Tran for the open sourcing her feature test code.
## Installation
python3 -m pip install feature-test

## utils.Utils 

<strong> class utils.Utils(X, columns) </strong> <br>
A collection of functions that enables users to get data on a dataframe or adjust it for testing. <br>

<strong> Parameters: </strong> <br>
<ul>
    <li><strong>X: pandas.DataFrame </strong> <br>
        <ul>    
        <li>A pandas.DataFrame containing the dataset <br></ul>
    <li> <strong>columns: List </strong> <br>
        <ul>
        <li>A list of strings correlating to features in a dataset.<br></ul></ul>
<strong> Methods </strong> <br>
_______________________________________________________________________________________<br>
<table>
    <tr>
        <td><strong>get_columns(X: pd.DataFrame)</strong></td>
        <td>Returns a list of column names in a dataframe.</td>
    </tr>
    <tr>
        <td><strong>exclude_columns(X: pd.DataFrame, columns: List)</strong></td>
        <td>Exclude a list of columns from a dataframe.</td>
    </tr> 
</table>
<br>

## tests.Correlation 

<strong> class tests.correlation(X, new_feature) </strong> <br>

A suite of functions that calculates and reports the correlation coefficient between features and all other features in a dataset. <br>
    
<strong> Parameters: </strong> <br>
<ul>
    <li><strong>X: pandas.DataFrame </strong> <br>
        <ul>    
        <li>A pandas.DataFrame containing the dataset <br></ul>
    <li> <strong>new_feature: string </strong> <br>
        <ul>
        <li>A string indicating the column in X to test against all other features <br></ul></ul>
<strong> Methods </strong> <br>
_______________________________________________________________________________________
<br>
<table>
    <tr>
        <td><strong>calc_corr(X: pd.DataFrame, new_feature: str)</strong></td>
        <td>Returns a dataframe with the correlation values for each new_feature/feature combination.</td>
    </tr>
    <tr>
        <td><strong>similar_corr(X: pd.DataFrame, new_feature: str)</strong></td> 
        <td>Returns a list of features highly correlated with the new_feature.</td>
    </tr>
    <tr>
        <td><strong>categorize_correlations(X: pd.DataFrame, correlation_threshold: float = 0.6)</strong></td> 
        <td>Returns a dataframe with the correlations categorized. Possible values are high, medium, and low.</td>
    </tr>
    <tr>
        <td><strong>get_correlations(X: pd.DataFrame, new_feature: str)</strong></td>
        <td>Returns a dataframe of new_feature/feature combinations, their correlations, and their correlation category.</td>
    </tr>
</table>

## tests.ChiSquare

<strong> class tests.ChiSquare(X, new_feature) </strong> <br>

Calculates the chi-squared statistic of the new feature against each categorical feature in a dataset. Also categorizes the chi-square result based on the p-value and effect size as measured by cramers v.<br>
    
<strong> Parameters: </strong> <br>
<ul>
    <li><strong>X: pandas.DataFrame </strong> <br>
        <ul>    
        <li>A pandas.DataFrame containing the dataset <br></ul>
    <li> <strong>new_feature: string </strong> <br>
        <ul>
        <li>A string indicating the column in X to test against all other features <br></ul></ul>
<strong> Methods </strong> <br>
_______________________________________________________________________________________
<br>
<table>
    <tr>
        <td><strong>calc_chi_sq(X: pd.DataFrame, new_feature: str)</strong></td>
        <td>Returns a dataframe that includes the chi-square result categorization.</td>
    </tr>
</table>

## tests.FeatureSelection

<strong> class tests.FeatureSelection(X, target) </strong> <br>

<br>
    
<strong> Parameters: </strong> <br>
<ul>
    <li><strong>X: pandas.DataFrame </strong> <br>
        <ul>    
        <li>A pandas.DataFrame containing the dataset <br></ul>
    <li> <strong>target: string </strong> <br>
        <ul>
        <li>A string indicating the prediction column<br></ul></ul>
<strong> Methods </strong> <br>
_______________________________________________________________________________________
<br>
<table>
    <tr>
        <td><strong>rfe_rankings(X: pd.DataFrame, target: str, classifier=None)</strong></td>
        <td>Returns a dataframe that includes the recursive feature elimination feature ranking.</td>
    </tr>
    <tr>
        <td><strong>lasso_rankings(X: pd.DataFrame, target: str)</strong></td>
        <td>Returns a dataframe that includes the linear model coefficients for features after lasso regularization.</td>
    </tr>
    <tr>
        <td><strong>ridge_coefficients(X: pd.DataFrame, target: str)</strong></td>
        <td>Returns a dataframe that includes the linear model coefficients for features after ridge regularization.</td>
    </tr>
    <tr>
        <td><strong>dtree_coefficients(X: pd.DataFrame, target: str)</strong></td>
        <td>Returns a dataframe that includes the decision tree model coefficients for features.</td>
    </tr>
    <tr>
        <td><strong>run_feature_classifiers(X: pd.DataFrame, target: str)</strong></td>
        <td>Returns a dataframe that includes the the results for rfe_rankings, lasso_rankings, ridge_rankings, and dtree_rankings.</td>
    </tr>
</table>

## Examples <br>
_______________________________________________________________________________________
```python
from pandas import util

from feature_test.utils import Utils
from feature_test.feature_tests import Correlation, FeatureSelection, ChiSq

# Create a test dataset
df= util.testing.makeDataFrame()
df.head()
```
| feature | A | B | C | D |
|---|---|---|---|---|
| lRhANYYD2r | 0.572559 | -1.409978 | 0.687618 | -0.923502 |
| YzYG07kY1O |	0.145629 |	-1.446946 |	-0.003526 |	0.304385 |
| cT3KK078Gt |	-1.007378 |	1.263980 |	1.107897 |	0.844689 |
| JW4Kg2EGVo |	0.536701 |	-1.477372 |	-0.866873 |	1.539458 |
| 2mucO1cf2Z |	-1.101875 |	0.518555 |	0.384916 |	-0.031403 |


```python
c = Utils.get_columns(df)
```
['A', 'B', 'C', 'D']


```python
corr_df = Correlation.calc_corr(df, 'A')
corr_df
```
| feature_1 | feature_2 | corr |
|-----------|-----------|------|
| A | B | 0.081662 |
| A | C | 0.203858 |
| A | D | 0.064999 |


```python
rep_df = Correlation.get_correlations(df, 'D')
rep_df
```
| feature_1 |	feature_2 |	corr |	corr_cat |
|-----------|-----------|------|-----------|
| A | B | 0.071466 | low |
| A | C | 0.105306 | low |
| A | D | 0.121130 | low |


```python
ChiSq.calc_chi_sq(df, 'A')
```
| feature_1 |	feature_2 |	chi_sq_cat |
|-----------|-----------|-----------|
| A | B | NOT SIGNIFICANT |
| A | C | NOT SIGNIFICANT |
| A | D | NOT SIGNIFICANT |

```python
FeatureSelection.rfe_rankings(df, 'A')
```
| feature |	rfe_rank |
|-----------|-----------|
| B | 3 |
| C | 1 |
| D | 2 |

```python
FeatureSelection.lasso_rankings(df, 'A')
```
| feature |	lasso_coef | lasso_importance |
|-----------|-----------|-----------|
| B | 0.0 | 2.0 |
| C | 0.0 | 2.0 |
| D | -0.0 | 2.0 |

```python
FeatureSelection.ridge_rankings(df, 'A')
```
| feature |	ridge_coef | ridge_importance
|-----------|-----------|-----------|
| B | 0.050871 | 3.0 |
| C | 0.096362 | 1.0 |
| D | -0.095220 | 2.0 |

```python
FeatureSelection.dtree_rankings(df, 'A')
```
| feature |	random_forest_coefficient | random_forest_importance |
|-----------|-----------|-----------|
| B | 0.323091 | 2.0 |
| C | 0.269673 | 3.0 |
| D | 0.407236 | 1.0 |

```python
FeatureSelection.dtree_rankings(df, 'A')
```
| feature |	rfe_rank | lasso_coef | lasso_importance | ridge_coef | ridge_importance | random_forest_coefficient | random_forest_importance |
|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| B | 3 | 0.0 | 2.0 | 0.050871 | 3.0 | 0.323091 | 2.0
| C | 1 | 0.0 | 2.0 | 0.096362 | 1.0 | 0.269673 | 3.0
| D | 2 | -0.0 | 2.0 | -0.095220 | 2.0 | 0.407236 | 1.0