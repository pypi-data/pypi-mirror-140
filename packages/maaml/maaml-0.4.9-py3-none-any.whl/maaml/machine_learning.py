from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import ShuffleSplit, train_test_split
from sklearn.preprocessing import label_binarize
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    cohen_kappa_score,
    roc_auc_score,
    classification_report,
)
from xgboost import XGBClassifier
import numpy as np
import time
from maaml.utils import save_csv, dict_transpose


class Evaluator:
    """A class to evaluate a dataset with 9 different machine learning models and saves the results in the working directory. includes an `evaluation` attribute, a `feature_importance_ranks` attribute in case the model allows for feature importance extraction, a `model_name` attribute, a `model` attribute and the `save_tag` attribute.
    It also includes useful static methods a `model_building` that produces a machine learning model class, a `model_evaluating` that does not include cross validation in the evaluation and a `feature_importance_ranking` that produce the `feature_importance_ranks`

    Args:
        * model_name (str or, optional): The choice of machine learning model can be an integer between `"0"` and `"9"` passed as a string or a name from the 9 available models such as `"LogisticRegression"`. Defaults to `"4"` which is `"ExtraTrees"` the best performing model in the most case.
        * parameter (str, optional): The standard parameter passed to the model as a string can be for exemple `"1000"` for the number of estimators to `"RandomForest"` or `"ExtraTrees"` or `"lbfgs"` the solver for `"LogisticRegression"`. Defaults to `None`.
        * features (pandas.DataFrame or array or numpy.array, optional): The features of the dataset in columns for the case that the dataset parameter is not provided. Defaults to `None`.
        * target (pandas.Series or array or numpy.array, optional): The classfication target in one column in the case that the dataset parameter is not provided . Defaults to `None`.
        * dataset (pandas.DataFrame or array or numpy.array, optional): A dataset that includes features in columns and a classfication target in one column. Defaults to `None`.
        * target_name (str, optional): The name of the classification target as a string. Defaults to `"target"`.
        * nb_splits (int, optional): The number of splits in case of cross validation. Defaults to `5`.
        * test_size (float, optional): The percentage of the test sample size as a float from the full dataset represented as `1` . Defaults to `0.3`.
        * full_eval (bool, optional): A full evaluation with all the available models in the case of `True` or the model chosen in the `model_name` parameter in the case of `False`. Defaults to `False`.
        * save_eval (bool, optional): saves the evaluation results in a new directory under the working directory in case of `True` and does not save the evaluation results in the case of `False`. Defaults to `False`.
        * save_tag (str, optional): The tag given to the created directory and the saved evaluation result, important in case of mutiple evaluation in the same directory to not overwite exiting results. Defaults to `None`.
        * preprocessing_alias (str, optional): The name for the applied dataset preprocessing as a string that is going to be displayed in the evaluation results. Defaults to `None`.
        * verbose (int, optional): An integer of the verbosity of the evaluation can be ``0`` or ``1``. Defaults to ``0``.
    """

    def __init__(
        self,
        model_name="4",
        parameter=None,
        features=None,
        target=None,
        dataset=None,
        target_name="target",
        nb_splits=5,
        test_size=0.3,
        full_eval=False,
        save_eval=False,
        save_tag=None,
        preprocessing_alias=None,
        verbose=0,
    ):
        """The constructor of the Evaluator class.

        Args:
            * model_name (str or, optional): The choice of machine learning model can be an integer between `"0"` and `"9"` passed as a string or a name from the 9 available models such as `"LogisticRegression"`. Defaults to `"4"` which is `"ExtraTrees"` the best performing model in the most case.
            * parameter (str, optional): The standard parameter passed to the model as a string can be for exemple `"1000"` for the number of estimators to `"RandomForest"` or `"ExtraTrees"` or `"lbfgs"` the solver for `"LogisticRegression"`. Defaults to `None`.
            * features (pandas.DataFrame or array or numpy.array, optional): The features of the dataset in columns for the case that the dataset parameter is not provided. Defaults to `None`.
            * target (pandas.Series or array or numpy.array, optional): The classfication target in one column in the case that the dataset parameter is not provided . Defaults to `None`.
            * dataset (pandas.DataFrame or array or numpy.array, optional): A dataset that includes features in columns and a classfication target in one column. Defaults to `None`.
            * target_name (str, optional): The name of the classification target as a string. Defaults to `"target"`.
            * nb_splits (int, optional): The number of splits in case of cross validation. Defaults to `5`.
            * test_size (float, optional): The percentage of the test sample size as a float from the full dataset represented as `1` . Defaults to `0.3`.
            * full_eval (bool, optional): A full evaluation with all the available models in the case of `True` or the model chosen in the `model_name` parameter in the case of `False`. Defaults to `False`.
            * save_eval (bool, optional): saves the evaluation results in a newly created directory under the working directory in case of `True`. Defaults to `False`.
            * save_tag (str, optional): The tag given to the created directory and the saved evaluation result, important in case of mutiple evaluation in the same directory to not overwite exiting results. Defaults to `None`.
            * preprocessing_alias (str, optional): The name for the applied dataset preprocessing as a string that is going to be displayed in the evaluation results. Defaults to `None`.
            * verbose (int, optional): An integer of the verbosity of the evaluation can be ``0`` or ``1``. Defaults to ``0``.
        """
        self.save_tag = "" if save_tag is None or save_tag == "" else f"_{save_tag}"
        PATH = f"ML_EVALUATION{self.save_tag}"
        if preprocessing_alias is not None:
            self.save_tag = f"_{preprocessing_alias}" + self.save_tag
        else:
            preprocessing_alias = ""
        self.model = i = 1
        self.evaluation = {}
        while True:
            if full_eval is False:
                self.model = self.model_building(model_name, parameter, verbose)
            elif full_eval is True:
                try:
                    self.model = self.model_building(i, parameter, verbose)
                    i += 1
                except ValueError:
                    print("full evaluation complete")
                    self.evaluation = dict_transpose(self.evaluation)
                    if save_eval is True:
                        self.tag = f"full_evaluation{self.save_tag}"
                        save_csv(self.evaluation, PATH, self.tag, verbose)
                    break

            if "SVC" in str(self.model):
                self.model_name = str(self.model).replace("SVC", "SVMClassifier")
            self.model_name = str(self.model).replace("()", "")
            if "XGB" in str(self.model):
                if parameter is not None:
                    self.model_name = f"XGBClassifier (n_estimators={parameter})"
                else:
                    self.model_name = "XGBClassifier"

            cross_evaluation = self.model_cross_validating(
                features,
                target,
                dataset,
                target_name,
                nb_splits,
                test_size,
                preprocessing_alias,
                verbose,
            )

            if not self.evaluation:
                self.evaluation = cross_evaluation
            else:
                for key in cross_evaluation:
                    self.evaluation[key].append(*cross_evaluation[key])
            if full_eval is False:
                self.evaluation = dict_transpose(self.evaluation)
                if save_eval is True:
                    self.tag = f"{self.model_name}{self.save_tag}_evaluation"
                    print("path is : \n", PATH)
                    print("tag is : \n", self.tag)
                    save_csv(self.evaluation, PATH, self.tag, verbose)

            try:
                self.feature_importance_ranks = self.features_importance_ranking(
                    self.model,
                    dataset,
                    target_name,
                    features,
                    target,
                    test_size,
                    verbose,
                )
            except AttributeError:
                self.feature_importance_ranks = None
                if verbose == 1:
                    print(
                        f"The {str(self.model)} does not allow the extraction of feature importance ranks\nSkipping action"
                    )
            if full_eval is False:
                break

    @staticmethod
    def model_building(model_name="4", parameter=None, verbose=0):
        """A static method to create a non trained machine learning model class.

        Args:
            * model_name (str or, optional): The choice of machine learning model can be an integer between `"0"` and `"9"` passed as a string or a name from the 9 available models such as `"LogisticRegression"`. Defaults to `"4"` which is `"ExtraTrees"` the best performing model in the most case.
            * parameter (str, optional): The standard parameter passed to the model as a string can be for exemple `"1000"` for the number of estimators to `"RandomForest"` or `"ExtraTrees"` or `"lbfgs"` the solver for `"LogisticRegression"`. Defaults to `None`.
            * verbose (int, optional): An integer of the verbosity of the model selection process can be ``0`` or ``1``. Defaults to ``0``.

        Returns:
            * class: a machine learning model class or a `"No model"` string in case of wrong selection of the `model_name` parameter.
        """
        model_name = str(model_name)
        if model_name == "1" or model_name == "DecisionTree":
            model = DecisionTreeClassifier()
        elif model_name == "2" or model_name == "RandomForest":
            if parameter is not None:
                parameter = int(parameter)
                model = RandomForestClassifier(n_estimators=parameter)
            else:
                model = RandomForestClassifier()
        elif model_name == "3" or model_name == "ExtraTree":
            model = ExtraTreeClassifier()
        elif model_name == "4" or model_name == "ExtraTrees":
            if parameter is not None:
                parameter = int(parameter)
                model = ExtraTreesClassifier(n_estimators=parameter)
            else:
                model = ExtraTreesClassifier()
        elif model_name == "5" or model_name == "KNeighbors":
            if parameter is not None:
                parameter = int(parameter)
                model = KNeighborsClassifier(n_neighbors=parameter)
            else:
                model = KNeighborsClassifier()
        elif model_name == "6" or model_name == "GaussianNB":
            model = GaussianNB()
        elif model_name == "7" or model_name == "SVM":
            if parameter is not None:
                parameter = str(parameter)
                model = svm.SVC(gamma=parameter)
            else:
                model = svm.SVC()
        elif model_name == "8" or model_name == "LogisticRegression":
            if parameter is not None:
                parameter = str(parameter)
                model = LogisticRegression(
                    solver=parameter, multi_class="auto", max_iter=1000
                )
            else:
                model = LogisticRegression(multi_class="auto", max_iter=1000)
        elif model_name == "9" or model_name == "MLPClassifier":
            if parameter is not None:
                parameter = int(parameter)
                model = MLPClassifier(max_iter=parameter)
            else:
                model = MLPClassifier()
        elif model_name == "10" or model_name == "XGboost":
            if parameter is not None:
                parameter = int(parameter)
                model = XGBClassifier(
                    n_estimators=parameter,
                    use_label_encoder=False,
                    verbosity=0,
                    silent=True,
                )
            else:
                model = XGBClassifier(use_label_encoder=False, verbosity=0, silent=True)
        else:
            error_message = "ERROR:wrong entry,you have 9 different classifiers, you could choose by number or by name"
            print(error_message)
            model = "No model"
        if verbose == 1:
            if "XGB" in str(model):
                print("\nThe XGBClassifier is selected")
            else:
                print(f"\nThe {str(model)} is selected")
        return model

    def model_cross_validating(
        self,
        features=None,
        target=None,
        dataset=None,
        target_name="target",
        nb_splits=5,
        test_size=0.3,
        preprocessing_alias=None,
        verbose=0,
    ):
        """A method for cross evaluating and training of a machine learning model class.

        Args:
            * features (pandas.DataFrame or array or numpy.array, optional): The features of the dataset in columns for the case that the dataset parameter is not provided. Defaults to `None`.
            * target (pandas.Series or array or numpy.array, optional): The classfication target in one column in the case that the dataset parameter is not provided . Defaults to `None`.
            * dataset (pandas.DataFrame or array or numpy.array, optional): A dataset that includes features in columns and a classfication target in one column. Defaults to `None`.
            * target_name (str, optional): The name of the classification target as a string. Defaults to `"target"`.
            * nb_splits (int, optional): The number of splits in case of cross validation. Defaults to `5`.
            * test_size (float, optional): The percentage of the test sample size as a float from the full dataset represented as `1` . Defaults to `0.3`.
            * preprocessing_alias (str, optional): The name for the applied dataset preprocessing as a string that is going to be displayed in the evaluation results. Defaults to `None`.
            * verbose (int, optional): An integer of the verbosity of the evaluation can be ``0`` or ``1``. Defaults to ``0``.

        Returns:
            dict: `cv_scores` the result cross validation evaluation scores.
        """
        start_time = time.perf_counter()
        if dataset is not None:
            X, Y = dataset.drop(target_name, axis=1), dataset[target_name]
        elif features is not None and target is not None:
            X, Y = features, target
        else:
            error_message = "ERROR: please enter a dataset with a target_name or you can enter features and target"
            print(error_message)
            return
        cv = ShuffleSplit(n_splits=nb_splits, test_size=test_size, random_state=10)
        acc_scores, pres_scores, rec_scores, f1, cokap_scores, roc_auc_scores = (
            [],
            [],
            [],
            [],
            [],
            [],
        )
        cv_scores = {
            "MLclassifier": [],
            "preprocessing": [],
            "execution time": [],
            "accuracy": [],
            "precision": [],
            "recall": [],
            "F1": [],
            "cohen_kappa": [],
            "roc_auc": [],
        }
        for train, test in cv.split(X, Y):
            classes = Y.unique()
            y_testb = label_binarize(Y[test], classes=classes)
            Y_values = Y.values
            Y_reshaped = Y_values.reshape(-1, 1)
            model = self.model
            pred = model.fit(X.loc[train], Y_values[train]).predict(X.loc[test])
            pred_reshaped = pred.reshape(-1, 1)
            acc_scores.append(accuracy_score(Y_values[test], pred, normalize=True))
            pres_scores.append(precision_score(Y_values[test], pred, average="macro"))
            rec_scores.append(recall_score(Y_values[test], pred, average="macro"))
            f1.append(f1_score(Y_values[test], pred, average="macro"))
            cokap_scores.append(cohen_kappa_score(Y_reshaped[test], pred_reshaped))
            roc_auc_scores.append(roc_auc_score(y_testb, pred_reshaped))
        end_time = time.perf_counter()
        cv_scores["MLclassifier"].append(self.model_name)
        cv_scores["preprocessing"].append(preprocessing_alias)
        cv_scores["execution time"].append(
            f"{((end_time-start_time) / nb_splits): .2f} (s)"
        )
        cv_scores["accuracy"].append(
            f"{np.mean(acc_scores):.4%} (+/- {np.std(acc_scores):.4%})"
        )
        cv_scores["precision"].append(
            f"{np.mean(pres_scores):.4%} (+/- {np.std(pres_scores):.4%})"
        )
        cv_scores["recall"].append(
            f"{np.mean(rec_scores):.4%} (+/- {np.std(rec_scores):.4%})"
        )
        cv_scores["F1"].append(f"{np.mean(f1):.4%} (+/- {np.std(f1):.4%})")
        cv_scores["cohen_kappa"].append(
            f"{np.mean(cokap_scores):.4%} (+/- {np.std(cokap_scores):.4%})"
        )
        cv_scores["roc_auc"].append(
            f"{np.mean(roc_auc_scores):.4%} (+/- {np.std(roc_auc_scores):.4%})"
        )
        if verbose == 1:
            print("\n\033[1mCross validation results: \033[0m")
            for i, v in cv_scores.items():
                print(f"{i}: {v[0]}")
        if verbose == 2:
            print(f"\nAccuracy evaluation for the separate splits:\n{acc_scores}")
            print(f"\nPrecision evaluation for the separate splits:\n{pres_scores}")
            print(f"\nRecall evaluation for the separate splits:\n{rec_scores}")
            print(f"\nF1 evaluation for the separate splits:\n{f1}")
            print(f"\nCohen_kappa evaluation for the separate splits:\n{cokap_scores}")
            print(f"\nRoc_Auc evaluation for the separate splits:\n{roc_auc_scores}")
        return cv_scores

    @staticmethod
    def features_importance_ranking(
        model=None,
        dataset=None,
        target_name="target",
        features=None,
        target=None,
        test_size=0.3,
        verbose=0,
    ):
        """A static method to evaluate the features importance and ranks them.

        Args:
            * model (class, optional): A machine learning model class that allowes for feature importance extraction, if left to `None` uses ExtraTreesClassifier as the default for the feature_importance_ranking. Defaults to `None`.
            * dataset (pandas.DataFrame or array or numpy.array, optional): A dataset that includes features in columns and a classfication target in one column. Defaults to `None`.
            * target_name (str, optional): The name of the classification target as a string. Defaults to `"target"`.
            * features (pandas.DataFrame or array or numpy.array, optional): The features of the dataset in columns for the case that the dataset parameter is not provided. Defaults to `None`.
            * target (pandas.Series or array or numpy.array, optional): The classfication target in one column in the case that the dataset parameter is not provided . Defaults to `None`.
            * test_size (float, optional): The percentage of the test sample size as a float from the full dataset represented as `1` . Defaults to `0.3`.
            * verbose (int, optional): An integer of the verbosity of the process, can be ``0`` or ``1``. Defaults to ``0``.

        Returns:
            * [pandas.DataFrame class]: The features names in one column and the importance percentage of every feature in another column.
        """
        if dataset is not None and target_name is not None:
            x = dataset.drop(target_name, axis=1)
            y = dataset[target_name].values
        elif dataset is None:
            x = features
            y = target.values
        X_train, X_test, y_train, y_test = train_test_split(
            x, y, test_size=test_size, random_state=10
        )
        if model is None:
            learner = ExtraTreesClassifier()
            model = str(learner)
            print(f"The default Classifier for feature importance ranking is {model}")
        else:
            learner = model
        learner = learner.fit(X_train, y_train)
        pred = learner.predict(X_test)

        if verbose == 1:
            f1score = f1_score(y_test, pred, average="macro")
            print(
                f"\nTrying to use {str(model)} for the feature ranking with an F1 score of : {f1score*100: .2f}%\n"
            )
        importances = learner.feature_importances_
        ranks = x.T.drop(x.index, axis=1)
        ranks["importance %"] = importances * 100
        ranks = ranks.sort_values("importance %")[::-1]
        if verbose == 1:
            print(
                f"The {len(ranks)} features importance is ranked successfully using the {str(learner)}"
            )
        return ranks

    @staticmethod
    def model_evaluating(
        model=None,
        dataset=None,
        target_name="target",
        features=None,
        targets=None,
        test_size=0.3,
        verbose=0,
    ):
        """A static method for evaluating a model and producing a classification report.

        Args:
            * model (class, optional): A machine learning model class, if left to `None` uses ExtraTreesClassifier as the default evaluator. Defaults to `None`.
            * dataset (pandas.DataFrame or array or numpy.array, optional): A dataset that includes features in columns and a classfication target in one column. Defaults to `None`.
            * target_name (str, optional): The name of the classification target as a string. Defaults to `"target"`.
            * features (pandas.DataFrame or array or numpy.array, optional): The features of the dataset in columns for the case that the dataset parameter is not provided. Defaults to `None`.
            * target (pandas.Series or array or numpy.array, optional): The classfication target in one column in the case that the dataset parameter is not provided . Defaults to `None`.
            * test_size (float, optional): The percentage of the test sample size as a float from the full dataset represented as `1` . Defaults to `0.3`.
            * verbose (int, optional): An integer of the verbosity of the evaluation, can be ``0`` or ``1``. Defaults to ``0``.

        Returns:
            * str: A string in a table structure for the classfication report.
        """
        if dataset is not None and target_name is not None:
            x = dataset.drop(target_name, axis=1)
            y = dataset[target_name].values
        elif dataset is None:
            x = features
            y = targets.values
        else:
            print("No data is provided for the evaluation")
        X_train, X_test, y_train, y_test = train_test_split(
            x, y, test_size=test_size, random_state=10
        )
        if model is None:
            learner = ExtraTreesClassifier()
            model = str(learner)
            print(
                f"You did not provide a classifier, the default Classifier is {model}"
            )
        else:
            learner = model
        learner = learner.fit(X_train, y_train)
        pred = learner.predict(X_test)
        results = classification_report(y_test, pred)
        if verbose == 1:
            print(results)
        return results


def main():
    from maaml.preprocessing import DataPreprocessor as dp
    from maaml.Datasets.UAH_dataset.time_series import UAHDatasetLoader

    raw = UAHDatasetLoader()
    processed = dp(data=raw.data, scaler=2)
    uahdataset = processed.ml_dataset
    alias = processed.scaler_name
    ml_evaluation = Evaluator(
        model_name=10,
        parameter=1000,
        dataset=uahdataset,
        verbose=1,
        preprocessing_alias=alias,
        full_eval=False,
        save_eval=True,
    )
    print(f"feature importance :\n{ml_evaluation.feature_importance_ranks}")


if __name__ == "__main__":
    main()
