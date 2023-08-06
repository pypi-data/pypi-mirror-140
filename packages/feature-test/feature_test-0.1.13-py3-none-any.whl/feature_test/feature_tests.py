import itertools as it
import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from typing import List

from feature_test.utils import Utils


class Correlation:
    """
    Suite of methods that calculates and reports the correlation coefficient between features and all other features in a dataset.
    
    Pearson’s correlation coefficient measures the statistical relationship, or association, between two continuous variables. It is known as the best method of measuring the association between variables of interest because it is based on the method of covariance. It gives information about the magnitude of the association, or correlation, as well as the direction of the relationship.
        
        High degree: If the coefficient value lies between ± correlation coefficient (default 0.6) and ± 1, then it is said to be a strong correlation. As one variable increases, the other variable tends to also increase (if positive) or decrease (if negative).
        
        Moderate degree: If the value lies between ± 0.30 and ± correlation coefficient (default 0.6), then it is said  to be a medium correlation. 
        
        Low degree: When the value lies below + .29, then it is said to be a small correlation.
    """

    def __init__(self):
        self.calc_corr()
        self.similar_corr()

    @classmethod
    def calc_corr(self, X: pd.DataFrame, new_feature: str) -> pd.DataFrame:
        """
        Returns a dataframe with the correlation values for each new_feature/feature combination. 
        """
        Utils._check_df_operand(X)
        Utils._check_str_operand(new_feature)
        Utils._check_str_in_df(X, new_feature)

        results = pd.DataFrame(columns=["feature_1", "feature_2", "corr"])

        c = Utils.get_columns(X)
        for f in c:
            if f != new_feature:
                corr = abs(X[new_feature].corr(X[f]))

                results = results.append(
                    {"feature_1": new_feature, "feature_2": f, "corr": corr,},
                    ignore_index=True,
                )
        return results

    @classmethod
    def similar_corr(self, X: pd.DataFrame, new_feature: str) -> List:
        """
        Returns a list of features highly correlated with the new_feature.
        """
        Utils._check_df_operand(X)
        Utils._check_str_operand(new_feature)
        Utils._check_str_in_df(X, new_feature)

        results = self.calc_corr(X, new_feature)
        similar_corr = results[results["corr"] >= 0.75]
        return similar_corr

    @classmethod
    def categorize_correlations(
        self, X: pd.DataFrame, correlation_threshold: float = 0.6
    ) -> pd.DataFrame:
        """
        Returns a dataframe with the correlations categorized. Possible values are high, medium, and low.
        """

        binInterval = [0, 0.3, correlation_threshold, 1]
        binLabels = ["low", "medium", "high"]

        X["corr_cat"] = pd.cut(X["corr"], binInterval, labels=binLabels)

        return X

    @classmethod
    def get_correlations(
        self, X: pd.DataFrame, new_feature: str
    ) -> pd.DataFrame:
        """
        Returns a dataframe of feature combinations and their correlations
        """

        corr_df = self.calc_corr(X, new_feature)
        cat_df = self.categorize_correlations(corr_df)

        return cat_df


class ChiSq:
    def __init__(self):
        self.calc_chi_sq()

    @classmethod
    def calc_chi_sq(self, X: pd.DataFrame, new_feature: str) -> pd.DataFrame:
        """
        Calculates the chi-squared statistic of the new feature against each categorical feature in a dataset.
        
        The Chi-Square test of independence is a statistical test to determine if there is a significant relationship between 2 categorical variables. 
        
        The Null hypothesis is that there is NO association between both variables. 
        The Alternate hypothesis says there is evidence to suggest there is an association between the two variables. 
        
        To reject the null hypothesis, the calculated P-Value needs to be below a defined threshold. Say, if we use an alpha of .05, if the p-value < 0.05 we reject the null hypothesis.
            
        Parameters
        --------
        X : dataframe (matrix) of features columns and single target column
        y : series (vector) of the target variable used to calculate --- with each feature
        """

        Utils._check_df_operand(X)
        Utils._check_str_operand(new_feature)
        Utils._check_str_in_df(X, new_feature)

        alpha = 0.05
        cramer_interpretation = {
            1: [0.10, 0.30, 0.50],
            2: [0.07, 0.21, 0.35],
            3: [0.06, 0.17, 0.29],
            4: [0.05, 0.15, 0.25],
            5: [0.05, 0.13, 0.22],
        }

        default_range = [0.10, 0.30, 0.50]

        results = pd.DataFrame(
            columns=["feature_1", "feature_2", "chi_sq_cat"]
        )

        for feature in X.loc[:, X.columns != new_feature].columns:
            feature_1 = X[new_feature]
            feature_2 = X[feature]
            crosstab = pd.crosstab(feature_1, feature_2)
            chi2, p, dof, expected = stats.chi2_contingency(crosstab)

            if len(pd.unique(feature_1)) == 1:
                cramers_v = 0
            elif len(pd.unique(feature_2)) == 1:
                cramers_v = 0
            else:
                cramers_v = round(
                    np.sqrt(
                        chi2
                        / (
                            len(feature_1)
                            * (
                                min(
                                    len(pd.unique(feature_1)),
                                    len(pd.unique(feature_2)),
                                )
                                - 1
                            )
                        )
                    ),
                    4,
                )

            if p < alpha:
                chi2_result = "SIGNIFICANT"
                effect_size_ranges = cramer_interpretation.get(
                    dof, default_range
                )
                if cramers_v < effect_size_ranges[0]:
                    chi2_result = chi2_result + " WITH NEGLIGIBLE EFFECT"
                elif cramers_v < effect_size_ranges[1]:
                    chi2_result = chi2_result + " WITH SMALL EFFECT"
                elif cramers_v < effect_size_ranges[2]:
                    chi2_result = chi2_result + " WITH MEDIUM EFFECT"
                elif cramers_v >= effect_size_ranges[2]:
                    chi2_result = chi2_result + " WITH LARGE EFFECT"
                else:
                    raise Exception(f"Invalid cramers v value: {cramers_v}")
            else:
                chi2_result = "NOT SIGNIFICANT"

            results = results.append(
                {
                    "feature_1": new_feature,
                    "feature_2": feature,
                    "chi_sq_cat": chi2_result,
                },
                ignore_index=True,
            )

        return results


class FeatureSelection:
    """
    A suite of methods that rank features based on their importance.
    """

    def __init__(self):
        self.rfe_rankings()
        self.lasso_coefficients()
        self.ridge_coefficients()
        self.dtree_coefficients()

    @classmethod
    def rfe_rankings(
        self, X: pd.DataFrame, target: str, classifier=None
    ) -> pd.DataFrame:
        """
        Returns a dataframe that includes the recursive feature elimination feature ranking.

        Given an external estimator that assigns weights to features (e.g., the coefficients of a linear model), the goal of recursive feature elimination (RFE) is to select features by recursively considering smaller and smaller sets of features. First, the estimator is trained on the initial set of features and the importance of each feature is obtained either through a coef_ attribute or through a feature_importances_attribute. Then, the least important features are pruned from current set of features. That procedure 
        is recursively repeated on the pruned set until the desired number of features to select is eventually reached.
        
        Best features are assigned rank 1.

        Parameters
        --------
        X : dataframe (matrix) of features columns and single target column
        target : sting representing the name of the target variable
        classifier: sklearn model object to calculate feature coefficient/feature importance
        """

        Utils._check_df_operand(X)
        Utils._check_str_operand(target)
        Utils._check_str_in_df(X, target)

        # Create objects for analysis
        y = X[target]
        X = Utils.exclude_columns(X, [target])

        # Construct Linear Regression model
        if not classifier:
            lr = LinearRegression(normalize=True)
        else:
            lr = classifier
        lr.fit(X, y)
        # Search 1-by-1 through features
        rfe = RFE(lr, n_features_to_select=1, verbose=0)
        rfe.fit(X, y)

        # Create a results dataframe with the RFE rank
        results_df = pd.DataFrame(X.columns)
        results_df["rfe_rank"] = rfe.ranking_

        # Rename the feature column
        results_df = results_df.rename(columns={0: "feature"})

        return results_df

    @classmethod
    def lasso_coefficients(self, X: pd.DataFrame, target: str) -> pd.DataFrame:
        """
        Returns a dataframe that includes the linear model coefficients for features after lasso regularization.
        
        L1 regularization adds a penalty α∑ni=1|wi| to the loss function (L1-norm). Since each non-zero coefficient adds to the penalty, it forces weak features to have zero as coefficients.

        Parameters
        --------
        X : dataframe (matrix) of features columns and single target column
        target : sting representing the name of the target variable
        """

        Utils._check_df_operand(X)
        Utils._check_str_operand(target)
        Utils._check_str_in_df(X, target)

        # Create objects for analysis
        y = X[target]
        X = Utils.exclude_columns(X, [target])

        lasso = Lasso(alpha=0.2, normalize=True)
        lasso.fit(X, y)

        # Create a results dataframe
        results_df = pd.DataFrame(X.columns)
        results_df["lasso_coef"] = lasso.coef_
        results_df["lasso_importance"] = (
            results_df["lasso_coef"].abs().rank(ascending=False)
        )

        # Rename the feature column
        results_df = results_df.rename(columns={0: "feature"})

        return results_df

    @classmethod
    def ridge_coefficients(self, X: pd.DataFrame, target: str) -> pd.DataFrame:
        """
        Returns a dataframe that includes the linear model coefficients for features after ridge regularization.
        
        Regularization of Ridge causes its weight to become very close to zero, but not zero. In contrast lasso can make weights equal to zero because of the types of regularization they use.

        Parameters
        --------
        X : dataframe (matrix) of features columns and single target column
        target : sting representing the name of the target variable
        """

        Utils._check_df_operand(X)
        Utils._check_str_operand(target)
        Utils._check_str_in_df(X, target)

        # Create objects for analysis
        y = X[target]
        X = Utils.exclude_columns(X, [target])

        ridge = Ridge(alpha=7)
        ridge.fit(X, y)

        # Create a results dataframe
        results_df = pd.DataFrame(X.columns)
        results_df["ridge_coef"] = ridge.coef_
        results_df["ridge_importance"] = (
            results_df["ridge_coef"].abs().rank(ascending=False)
        )

        # Rename the feature column
        results_df = results_df.rename(columns={0: "feature"})

        return results_df

    @classmethod
    def dtree_coefficients(self, X: pd.DataFrame, target: str) -> pd.DataFrame:
        """
        Returns a dataframe that includes the decision tree model coefficients and rankings for features.
        
        A random forest is a meta estimator that fits a number of decision tree classifiers on various sub-samples of the dataset and uses averaging to improve the predictive accuracy and control over-fitting. The sub-sample size is controlled with the max_samples parameter if bootstrap=True (default), otherwise the whole dataset is used to build each tree.
        
        Parameters
        --------
        X : dataframe (matrix) of features columns and single target column
        target : sting representing the name of the target variable
        """

        Utils._check_df_operand(X)
        Utils._check_str_operand(target)
        Utils._check_str_in_df(X, target)

        # Create objects for analysis
        y = X[target].astype(int)
        X = Utils.exclude_columns(X, [target])

        sel = SelectFromModel(
            RandomForestClassifier(n_estimators=100, n_jobs=-1)
        )
        sel.fit(X, y)

        # Create a results dataframe
        results_df = pd.DataFrame(X.columns)
        results_df[
            "random_forest_coefficient"
        ] = sel.estimator_.feature_importances_
        results_df["random_forest_importance"] = (
            results_df["random_forest_coefficient"].abs().rank(ascending=False)
        )

        # Rename the feature column
        results_df = results_df.rename(columns={0: "feature"})

        return results_df

    @classmethod
    def run_feature_classifiers(
        self, X: pd.DataFrame, target: str
    ) -> pd.DataFrame:
        """
        Returns a dataframe that includes the the results for rfe_rankings, lasso_rankings, ridge_rankings, and dtree_rankings.
        
        Parameters
        --------
        X : dataframe (matrix) of features columns and single target column
        target : sting representing the name of the target variable
        """

        rfe_results = FeatureSelection.rfe_rankings(X, target)
        l1_results = FeatureSelection.lasso_coefficients(X, target)
        l2_results = FeatureSelection.ridge_coefficients(X, target)
        dtree_results = FeatureSelection.dtree_coefficients(X, target)

        results = pd.merge(rfe_results, l1_results, on="feature")
        results = pd.merge(results, l2_results, on="feature")
        results = pd.merge(results, dtree_results, on="feature")

        return results
