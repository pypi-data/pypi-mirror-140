from .functions import cohenD
import numpy as np
from scipy.special import logit, expit
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LogisticRegression
import math
import pandas.api.types as ptypes
import seaborn as sns
sns.set(rc={'figure.figsize': (10, 8)}, font_scale=1.3)


class PsmPy:
    """
    Matcher Class -- Match data for an observational study.
    Parameters
    ----------
    data : pd.DataFrame
        Data representing the treated group
    treatment : str
        Column representing the control group
    indx : str
        Name of index column
    exclude : list (optional)
        List of variables to ignore in regression/matching.
    target : str (optional)
        Outcome variable of interest, will ignore in regression/matching
    ----------    
    """

    def __init__(self, data, treatment, indx, exclude=[], target='outcome'):
        # variables generated during matching
        # assign unique indices to test and control
        self.data = data.dropna(axis=0, how="all")  # drop all NAN rows
        self.data = data.dropna(axis=1, how="all")  # drop all NAN col
        self.data[treatment] = self.data[treatment].astype(
            int)  # need binary 0, 1
        self.control_color = "#1F77B4"
        self.treatment_color = "#FF7F0E"
        self.treatment = treatment
        self.target = target
        self.indx = indx
        self.exclude = exclude + [self.treatment] + [self.indx]
        self.drop = exclude
        self.xvars = [i for i in self.data.columns if i not in self.exclude]
        self.keep_cols = [self.indx] + self.xvars
        self.data = self.data.drop(labels=self.drop, axis=1)
        self.model_accuracy = []
        self.dataIDindx = self.data.set_index(indx)
        assert all(ptypes.is_numeric_dtype(
            self.dataIDindx[xvar]) for xvar in self.xvars), "Only numeric dtypes allowed"
        self.treatmentdf = self.dataIDindx[self.dataIDindx[treatment] == 1]
        self.controldf = self.dataIDindx[self.dataIDindx[treatment] == 0]
        self.treatmentn = len(self.treatmentdf)
        self.controln = len(self.controldf)

    def logistic_ps(self, balance=True):
        """
        Fits logistic regression model(s) used for generating propensity scores
        Parameters
        ----------
        balance : bool
            Should balanced datasets be used?
            (n_control == n_test is default when balance = True)
        Returns
        predicted_data : pd.DataFrame
            DataFrame with propensity scores and logit propensity scores
        -------
        """
        if self.treatmentn < self.controln:
            minority, majority = self.treatmentdf, self.controldf
        elif self.treatmentn > self.controln:
            minority, majority = self.controldf, self.treatmentdf
        else:
            minority, majority = self.controldf, self.treatmentdf
        # if user wishes cases to be balanced:
        if balance == True:
            def chunker(seq, size):
                return (seq[pos:pos + size] for pos in range(0, len(seq), size))

            even_folds = math.floor(len(majority)/minority.shape[0])
            majority_trunc_len = even_folds*minority.shape[0]
            majority_len_diff = majority.shape[0] - majority_trunc_len
            majority_trunc = majority[0:majority_trunc_len]

            appended_data = []
            for i in chunker(majority_trunc, minority.shape[0]):
                joint_df = pd.concat([i, minority])
                treatment = joint_df[self.treatment]
                df_cleaned = joint_df.drop([self.treatment], axis=1)
                logistic = LogisticRegression(solver='liblinear')
                logistic.fit(df_cleaned, treatment)
                pscore = logistic.predict_proba(df_cleaned)[:, 1]
                df_cleaned['propensity_score'] = pscore
                df_cleaned['propensity_logit'] = np.array(
                    logit(xi) for xi in pscore)
                appended_data.append(df_cleaned)
            # if some of majority class leftover after the folding for training:
            if majority_len_diff != 0:
                majority_leftover = majority[majority_trunc_len:]
                len_major_leftover = len(majority_leftover)
                if len_major_leftover <= 80:
                    need_2_sample_more_majorclass = 80 - len_major_leftover
                    # select the remaining ones from major class:
                    majority_leftover1 = majority[majority_trunc_len:]
                    # select the ones that have already been processed:
                    majority_already_folded = majority[:majority_trunc_len]
                    #self.majority_already_folded = majority_already_folded
                    # sample from the ones already folded over above to get major class of 80 for last fold:
                    majority_leftover2 = majority_already_folded.sample(
                        n=need_2_sample_more_majorclass)
                    # add the leftover to the additional that need to be sampled to get to 40
                    majority_leftover_all = pd.concat(
                        [majority_leftover1, majority_leftover2])
                    # sample a macthing 80 from the minor class
                    minority_sample = minority.sample(n=80)
                    joint_df = pd.concat(
                        [majority_leftover_all, minority_sample])
                    treatment = joint_df[self.treatment]
                    df_cleaned = joint_df.drop([self.treatment], axis=1)
                    logistic = LogisticRegression(solver='liblinear')
                    logistic.fit(df_cleaned, treatment)
                    pscore = logistic.predict_proba(df_cleaned)[:, 1]
                    df_cleaned['propensity_score'] = pscore
                    df_cleaned['propensity_logit'] = np.array(
                        logit(xi) for xi in pscore)
                    appended_data.append(df_cleaned)
                else:
                    majority_extra = majority[majority_trunc_len:]
                    minority_sample = minority.sample(n=majority_len_diff)
                    joint_df = pd.concat([majority_extra, minority_sample])
                    treatment = joint_df[self.treatment]
                    df_cleaned = joint_df.drop([self.treatment], axis=1)
                    logistic = LogisticRegression(solver='liblinear')
                    logistic.fit(df_cleaned, treatment)
                    pscore = logistic.predict_proba(df_cleaned)[:, 1]
                    df_cleaned['propensity_score'] = pscore
                    df_cleaned['propensity_logit'] = np.array(
                        logit(xi) for xi in pscore)
                    appended_data.append(df_cleaned)
            else:
                pass
            predicted_data_repeated = pd.concat(appended_data)
            predicted_data_repeated_reset = predicted_data_repeated.reset_index()

            # pull repeated minority class out to average calculations for prop scores
            repeated_data = predicted_data_repeated_reset[predicted_data_repeated_reset.duplicated(
                subset=self.indx, keep=False)]
            unique_ids = repeated_data[self.indx].unique()

            mean_repeated = []
            for repeated_id in unique_ids:
                temp_repeat_df = predicted_data_repeated_reset[
                    predicted_data_repeated_reset[self.indx] == repeated_id]
                prop_mean = temp_repeat_df['propensity_score'].mean()
                prop_logit_mean = logit(prop_mean)
                short_entry = temp_repeat_df[0:1]
                short_entry_rst = short_entry.reset_index(drop=True)
                short_entry_rst.at[0, 'propensity_score'] = prop_mean
                short_entry_rst.at[0, 'propensity_logit'] = prop_logit_mean
                mean_repeated.append(short_entry_rst)
            filtered_repeated = pd.concat(mean_repeated)

            # remove all duplicated minority class from folded df to be rejoined with the fixed values
            not_repeated_predicted = predicted_data_repeated_reset.drop_duplicates(
                subset=self.indx, keep=False)
            predicted_data_ps = pd.concat(
                [filtered_repeated, not_repeated_predicted]).reset_index(drop=True)

            # merge with treatment df
            treatment_dfonly = self.dataIDindx[[self.treatment]].reset_index()
            self.predicted_data = pd.merge(
                predicted_data_ps, treatment_dfonly, how='inner', on=self.indx)
            predicted_data_control = self.predicted_data[self.predicted_data[self.treatment] == 0]
            predicted_data_treatment = self.predicted_data[self.predicted_data[self.treatment] == 1]

            # return predicted_data
        # If user does not wish cases to be balanced
        else:
            joint_df = pd.concat([majority, minority])
            treatment = joint_df[self.treatment]
            df_cleaned = joint_df.drop([self.treatment], axis=1)
            logistic = LogisticRegression(solver='liblinear')
            logistic.fit(df_cleaned, treatment)
            pscore = logistic.predict_proba(df_cleaned)[:, 1]
            df_cleaned['propensity_score'] = pscore
            df_cleaned['propensity_logit'] = np.array(
                logit(xi) for xi in pscore)
            predicted_data_reset = df_cleaned.reset_index()

            # merge with treatment df
            treatment_dfonly = self.dataIDindx[[self.treatment]].reset_index()
            self.predicted_data = pd.merge(
                predicted_data_reset, treatment_dfonly, how='inner', on='patient_ir_id')
            predicted_data_control = self.predicted_data[self.predicted_data[self.treatment] == 0]
            predicted_data_treatment = self.predicted_data[self.predicted_data[self.treatment] == 1]

            # return predicted_data

    def knn_matched(self, matcher, replacement=False, caliper=None):
        """
        knn_matched -- Match data using k-nn algorithm
        Parameters
        ----------
        matcher : str
           string that will used to match - propensity score or proppensity logit
        replacement : bool
           Want to match with or without replacement
        caliper_multip : float
           caliper multiplier for allowable matching
        Returns
        balanced_match : pd.DataFrame
            DataFrame with column with matched ID based on k-NN algorithm
        """
        matcher = matcher
        predicted_data_control = self.predicted_data[self.predicted_data[self.treatment] == 0]
        predicted_data_treatment = self.predicted_data[self.predicted_data[self.treatment] == 1]

        # if caliper_multip is not None:
        # caliper = np.std(predicted_data_control[matcher]) * caliper_multip
        # else:
        # pass

        if len(predicted_data_treatment) < len(predicted_data_control):
            min_pred, major_pred = predicted_data_treatment, predicted_data_control
            major_pred_rstindx = major_pred.reset_index(drop=True)
            minor_pred_rstindx = min_pred.reset_index(drop=True)
        elif len(predicted_data_treatment) > len(predicted_data_control):
            min_pred, major_pred = predicted_data_control, predicted_data_treatment
            major_pred_rstindx = major_pred.reset_index(drop=True)
            minor_pred_rstindx = min_pred.reset_index(drop=True)
        else:
            min_pred, major_pred = predicted_data_control, predicted_data_treatment
            major_pred_rstindx = major_pred.reset_index(drop=True)
            minor_pred_rstindx = min_pred.reset_index(drop=True)

        # need to fit KNN with larger class
        knn = NearestNeighbors(n_neighbors=len(major_pred_rstindx), p=2)
        knn.fit(major_pred_rstindx[[matcher]].to_numpy())
        distances, indexes = knn.kneighbors(
            minor_pred_rstindx[[matcher]], n_neighbors=len(major_pred_rstindx))

        def condition_caliper(x, caliper):
            return x <= caliper

        # remove elements outside of radius:
        if caliper is not None:
            for dist in distances[:, :]:
                dist = np.ndarray.tolist(dist)
                self.output_dist_indices = [idx for idx, element in enumerate(
                    dist) if condition_caliper(element, caliper)]
            if replacement == False:
                indexes_for_match = []
                elements_to_remove = []
                for row in indexes[:, :]:
                    row = np.ndarray.tolist(row)
                    row_distclean = [row[index]
                                     for index in self.output_dist_indices]
                    for element in elements_to_remove:
                        if element in row_distclean:
                            row_distclean.remove(element)
                    indexes_for_match.append(row_distclean[0])
                    elements_to_remove.append(row_distclean[0])
            else:
                indexes_for_match = []
                for row in indexes[:, :]:
                    row = np.ndarray.tolist(row)
                    row_distclean = [row[index]
                                     for index in self.output_dist_indices]
                    indexes_for_match.append(row_distclean[0])
        else:
            # n_neighbors=len(major_pred_rstindx)
            if replacement == False:
                indexes_for_match = []
                elements_to_remove = []
                for row in indexes[:, :]:
                    row = np.ndarray.tolist(row)
                    for element in elements_to_remove:
                        if element in row:
                            row.remove(element)
                    indexes_for_match.append(row[0])
                    elements_to_remove.append(row[0])
            else:
                indexes_for_match = []
                for row in indexes[:, :]:
                    row = np.ndarray.tolist(row)
                    indexes_for_match.append(row[0])

        ID_match = []
        for idxxx in indexes_for_match:
            match = major_pred_rstindx.loc[idxxx, self.indx]
            ID_match.append(match)

        major_matched = major_pred_rstindx.take(indexes_for_match)
        self.df_matched = pd.concat(
            [minor_pred_rstindx, major_matched], axis=0, ignore_index=True)
        minor_pred_rstindx['matched_ID'] = ID_match
        self.matched_ids = minor_pred_rstindx[[self.indx, 'matched_ID']]

    def plot_match(self, matched_entity='propensity_logit', Title='Side by side matched controls', Ylabel='Number of patients', Xlabel='propensity logit', names=['treatment', 'control'], colors=['#E69F00', '#56B4E9'], save=False):
        """
        knn_matched -- Match data using k-nn algorithm
        Parameters
        ----------
        matcher : str
           string that will used to match - propensity score or proppensity logit
        replacement : bool
           Want to match with or without replacement
        caliper : float
           caliper multiplier for allowable matching
        Returns
        balanced_match : pd.DataFrame
            DataFrame with column with matched ID based on k-NN algorithm
        """
        dftreat = self.df_matched[self.df_matched[self.treatment] == 1]
        dfcontrol = self.df_matched[self.df_matched[self.treatment] == 0]
        x1 = dftreat[matched_entity]
        x2 = dfcontrol[matched_entity]
        # Assign colors for each airline and the names
        colors = colors
        names = names
        sns.set_style("white")
        # Make the histogram using a list of lists
        # Normalize the flights and assign colors and names
        plt.hist([x1, x2], color=colors, label=names)
        # Plot formatting
        plt.legend()
        plt.xlabel(Xlabel)
        plt.ylabel(Ylabel)
        plt.title(Title)
        if save == True:
            plt.savefig('propensity_match.png', dpi=250)
        else:
            pass

    def effect_size_plot(self, title='Standardized Mean differences accross covariates before and after matching',
                         before_color='#FCB754', after_color='#3EC8FB', save=False):
        """
        effect_size_plot -- Plot effect size on each variable before and after matching 
        Parameters
        ----------
        title : str (optional)
           Title the graphic generated 
        before_color : str (hex)
           color for the before matching effect size per variable
        after_color : str (hex)
           color for the after matching effect size per variable
        save : bool
            Save graphic or not (default = False)
        Returns
        Seaborn graphic
        """
        df_preds_after = self.df_matched[[self.treatment] + self.xvars]
        df_preds_b4 = self.data[[self.treatment] + self.xvars]
        df_preds_after_float = df_preds_after.astype(float)
        df_preds_b4_float = df_preds_b4.astype(float)

        data = []
        for cl in self.xvars:
            try:
                data.append([cl, 'before', cohenD(
                    df_preds_b4_float, self.treatment, cl)])
            except:
                data.append([cl, 'before', 0])
            try:
                data.append([cl, 'after', cohenD(
                    df_preds_after_float, self.treatment, cl)])
            except:
                data.append([cl, 'after', 0])
        self.effect_size = pd.DataFrame(
            data, columns=['Variable', 'matching', 'Effect Size'])
        sns.set_style("white")
        sns_plot = sns.barplot(data=self.effect_size, y='Variable', x='Effect Size', hue='matching', palette=[
                               before_color, after_color], orient='h')
        sns_plot.set(title=title)
        if save == True:
            sns_plot.figure.savefig(
                'effect_size.png', dpi=250, bbox_inches="tight")
        else:
            pass
