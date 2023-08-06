from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    MaxAbsScaler,
    RobustScaler,
    QuantileTransformer,
    PowerTransformer,
    Normalizer,
)
from sklearn.decomposition import PCA
from maaml.utils import (
    save_csv,
    DataFrame,
    window_stepping,
    save_parquet,
    transposing,
    columns_mean,
)
import time


class DataPreprocessor:
    """A class for Data preprocessing specialized in time series data analysis from dataframes. includes these attributes: `raw_dataset`, `filtered_dataset` ,`numeric_dataset` ,`scaled_dataset` ,`scaler_name` ,`ml_dataset` ,`features` ,`target` ,`target_ohe` ,`preprocessed_dataset` ,
    `dl_dataset` and in the case of window stepping `windowed_dataset` ,`ml_dataset_w` ,`features_w` ,`target_w` ,`target_ohe_w` ,`preprocessed_dataset_w` ,`dl_dataset_w`.
    It also includes useful static methods a `uahdataset_loading` for loading the UAHdataset,`label_encoding` for encoding categorical data,`data_scaling` for scaling the data,`one_hot_encoding` for one hot encoding and `window_stepping` for window stepping.

    Args:
    * data (pandas.DataFrame or array or numpy.array, optional): A dataframe that includes features in columns and a target in one column with a name that match the target provided in the `target_name`. Defaults to `None`.
    * target_name (str, optional): The name of the dataset target as a string. Defaults to `"target"`.
    * scaler (str, optional): selects the scaling technique used as integers from `"0"` to `"8"` passed as strings, or the name of the scaling technique such as `"minmax"` or `"normalizer"`. Defaults to no scaling with the value `"0"`.
    * droped_columns (list, optional): list of strings with the name of the columns to be removed or droped from the dataset after preprocessing. Defaults to `None`.
    * no_encoding_columns (list, optional): list of strings with the name of columns that will not be included in the label encoding process of cataegorical data. Defaults to `None`.
    * no_scaling_columns (list, optional): list of strings with the name of columns not to be included in the data scaling. Defaults to `None`.
    * nb_pca_component (int,optional): The number of component for Prinicipal Component Analysis, if set to `None` does not perform PCA. Defaults to `None`.
    * window_size (int, optional): the size of the window in the case of window stepping the data, in case of `None` will not perform the window stepping. Defaults to `None`.
    * step (int, optional): The length of the step for window stepping,if `None` will not perform the window stepping, if smaller than `window_size` will result in overlapping windows, if equal to `window_size` performs standard window stepping, if bigger will skip some rows (not recommended). Defaults to `None`.
    * window_transformation (bool, optional): in case of True applies the function in `window_transformation_function` parameter to the window. Defaults to `False`.
    * transformation_fn (function, optional): A function to be applied to the window, it takes the window dataframe as argument. Defaults to applying mean mean values on the columns with: `columns_mean`.
    * transformation_kwargs (dict,optional): A dictionary of keyword arguments (function arguments names and their values) specific to the function introduced in the transformation_fn, if not set will not pass any arguments to the function.Defaults to `None`.
    * save_to (str, optional): Can be `"csv"` or `"parquet"` or `None` if set to `"csv"` or `"parquet"` will save to the corresponding format in a newly created directory under the working directory, the preprocessed dataset with an ML specified and DL specified datasets, and windowed data for each case if window stepping is applied, if set to `None` will not save anything. Defaults to `None`.
    * save_tag (str, optional): add a custom tag to the name of the files to be saved in the case of save_dataset is `True`. Defaults to `"dataset"`.
    * verbose (int, optional): An integer of the verbosity of the process can be ``0`` or ``1``. Defaults to ``0``.
    """

    def __init__(
        self,
        data=None,
        target_name="target",
        scaler="0",
        droped_columns=None,
        no_encoding_columns=None,
        no_scaling_columns=None,
        nb_pca_component=None,
        window_size=None,
        step=None,
        window_transformation=False,
        window_transformation_function=columns_mean,
        transformation_kwargs=None,
        save_to=None,
        save_tag="dataset",
        verbose=0,
    ):
        """A constructor for the DataProcessor class

        Args:

            * data (pandas.DataFrame or array or numpy.array, optional): A dataframe that includes features in columns and a target in one column with a name that match the target provided in the `target_name`. Defaults to `None`.
            * target_name (str, optional): The name of the dataset target as a string. Defaults to `"target"`.
            * scaler (str, optional): selects the scaling technique used as integers from `"0"` to `"8"` passed as strings, or the name of the scaling technique such as `"minmax"` or `"normalizer"`. Defaults to no scaling with the value `"0"`.
            * droped_columns (list, optional): list of strings with the name of the columns to be removed or droped from the dataset after preprocessing. Defaults to `None`.
            * no_encoding_columns (list, optional): list of strings with the name of columns that will not be included in the label encoding process of cataegorical data. Defaults to `None`.
            * no_scaling_columns (list, optional): list of strings with the name of columns not to be included in the data scaling. Defaults to `None`.
            * nb_pca_component (int,optional): The number of component for Prinicipal Component Analysis, if set to `None` does not perform PCA. Defaults to `None`.
            * window_size (int, optional): the size of the window in the case of window stepping the data, in case of `None` will not perform the window stepping. Defaults to `None`.
            * step (int, optional): The length of the step for window stepping,if `None` will not perform the window stepping, if smaller than `window_size` will result in overlapping windows, if equal to `window_size` performs standard window stepping, if bigger will skip some rows (not recommended). Defaults to `None`.
            * window_transformation (bool, optional): in case of True applies the function in `window_transformation_function` parameter to the window. Defaults to `False`.
            * transformation_fn (function, optional): A function to be applied to the window, it takes the window dataframe as argument. Defaults to applying mean mean values on the columns with: `columns_mean`.
            * transformation_kwargs (dict,optional): A dictionary of keyword arguments (function arguments names and their values) specific to the function introduced in the transformation_fn, if not set will not pass any arguments to the function.Defaults to `None`.
            * save_to (str, optional): Can be `"csv"` or `"parquet"` or `None` if set to `"csv"` or `"parquet"` will save to the corresponding format in a newly created directory under the working directory, the preprocessed dataset with an ML specified and DL specified datasets, and windowed data for each case if window stepping is applied, if set to `None` will not save anything. Defaults to `None`.
            * save_tag (str, optional): add a custom tag to the name of the files to be saved in the case of save_dataset is `True`. Defaults to `"dataset"`.
            * verbose (int, optional): An integer of the verbosity of the process can be ``0`` or ``1``. Defaults to ``0``.
        """
        start_time = time.perf_counter()
        self.raw_dataset = DataFrame(data)
        droped_columns = [] if droped_columns is None else droped_columns
        self.filtered_dataset = self.raw_dataset.drop(labels=droped_columns, axis=1)
        no_encoding_columns = [] if no_encoding_columns is None else no_encoding_columns
        self.numeric_dataset = self.filtered_dataset.copy(deep=True)
        for column in self.numeric_dataset.columns:
            if column in no_encoding_columns:
                if verbose == 1:
                    print(
                        f"skipping \033[1m{column}\033[0m label encoding for being in the no_encoding_columns"
                    )
            else:
                if (
                    self.numeric_dataset.dtypes[column] != float
                    and self.numeric_dataset.dtypes[column] != int
                ):
                    self.numeric_dataset = self.label_encoding(
                        self.numeric_dataset, target=column, verbose=verbose
                    )
        no_scaling_columns = [] if no_scaling_columns is None else no_scaling_columns
        if target_name not in no_scaling_columns:
            no_scaling_columns.append(target_name)
            print(
                f"\033[1mAutomatically adding the target_name column '{target_name}' to the no_scaling_columns.\033[0m"
            )
        self.scaled_dataset, self.scaler_name = self.data_scaling(
            self.numeric_dataset,
            excluded_axis=no_scaling_columns,
            scaler=scaler,
            verbose=verbose,
        )
        if nb_pca_component:
            self.pca_decomposed_dataset = self.pca_decomposition(
                self.scaled_dataset,
                excluded=target_name,
                nb_components=nb_pca_component,
                verbose=verbose,
            )
        else:
            if verbose == 1:
                print("No PCA decomposition done.")
            self.pca_decomposed_dataset = self.scaled_dataset
        if verbose == 1:
            print("Automatically performing a data Cleanup from missing values.")
        self.ml_dataset = self.pca_decomposed_dataset.dropna()
        self.features = self.ml_dataset.drop(target_name, axis=1)
        self.target = self.ml_dataset[target_name]
        self.target_ohe = self.one_hot_encoding(
            self.ml_dataset, target=target_name, verbose=verbose
        )
        self.preprocessed_dataset = self.ml_dataset.copy(deep=True)
        for i in self.target_ohe.columns:
            column_name = f"{target_name} {i}"
            self.preprocessed_dataset[column_name] = self.target_ohe[i]
        self.dl_dataset = self.preprocessed_dataset
        PATH = "preprocessed_dataset"
        if save_to == "csv":
            save_csv(self.ml_dataset, PATH, f"ml_{save_tag}", verbose=verbose)
            save_csv(self.dl_dataset, PATH, f"dl_{save_tag}", verbose=verbose)
        if save_to == "parquet":
            save_parquet(self.ml_dataset, PATH, f"ml_{save_tag}", verbose=verbose)
            save_parquet(self.dl_dataset, PATH, f"dl_{save_tag}", verbose=verbose)
        if window_size and step:
            if verbose == 1:
                print(
                    "\n\033[1mThe window stepping can take some time depending on the dataset \033[0m"
                )
            self.windowed_dataset = self.ml_dataset.copy(deep=True)
            self.windowed_dataset = window_stepping(
                self.windowed_dataset,
                window_size=window_size,
                step=step,
                window_transformation=window_transformation,
                transformation_fn=window_transformation_function,
                transformation_kwargs=transformation_kwargs,
                verbose=verbose,
            )
            self.ml_dataset_w = self.windowed_dataset.dropna()
            self.features_w = self.ml_dataset_w.drop(target_name, axis=1)
            if window_transformation == True:
                self.target_w = self.ml_dataset_w[target_name].round()
            else:
                self.target_w = self.ml_dataset_w[target_name]
            self.target_ohe_w = self.one_hot_encoding(
                self.target_w, target=target_name, verbose=verbose
            )
            self.preprocessed_dataset_w = self.ml_dataset_w.copy(deep=True)
            for i in self.target_ohe_w.columns:
                column_name = f"{target_name} {i}"
                self.preprocessed_dataset_w[column_name] = self.target_ohe_w[i]
            self.dl_dataset_w = self.preprocessed_dataset_w
            if save_to == "csv":
                save_csv(
                    self.ml_dataset_w,
                    PATH,
                    f"ml_{save_tag}_w({window_size})_s({step})",
                    verbose=verbose,
                )
                save_csv(
                    self.dl_dataset_w,
                    PATH,
                    f"dl_{save_tag}_w({window_size})_s({step})",
                    verbose=verbose,
                )
            if save_to == "parquet":
                save_parquet(
                    self.ml_dataset_w,
                    PATH,
                    f"ml_{save_tag}_w({window_size})_s({step})",
                    verbose=verbose,
                )
                save_parquet(
                    self.dl_dataset_w,
                    PATH,
                    f"dl_{save_tag}_w({window_size})_s({step})",
                    verbose=verbose,
                )
        self.exec_time = time.perf_counter() - start_time
        self.preprocessing_info = self.scaler_name + f"({self.exec_time:.2f} s)"
        if verbose == 1:
            print(
                f"\n\033[1m========= DATA PREPROCESSED SUCCESSFULLY [ ET: {self.exec_time:.2f} (s) ] =========\033[0m\n"
            )

    @staticmethod
    def label_encoding(data, target, verbose=1):
        """A static method to to convert categorical data column to numeric data via label encoding.

        Args:
            * data (pandas.DataFrame or array or numpy.array): An array of data with a column of categorical data.
            * target ([str]): The name of the column to be converted.
            * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``1``.

        Returns:
            * pandas.DataFrame: the data with the cateorical data column converted to numeric data.
        """
        data = DataFrame(data)
        df = DataFrame(data)
        encoder = LabelEncoder()
        if target in data.columns:
            if verbose == 1:
                print(
                    f"encoding the \033[1m{target}\033[0m column. The target labels are: {data[target].unique()} "
                )
            df[target] = encoder.fit_transform(data[target])
            if verbose == 1:
                print(f"The target labels after encoding : {df[target].unique()}")
        else:
            raise KeyError(f"The target column '{target}' does not exist in data")
        return df

    @staticmethod
    def data_scaling(data, excluded_axis=[], scaler="minmax", verbose=1):
        """A static method to scale the data using 8 diffrent scaling techniques or returning the raw data with all column values conveted to floats.

        Args:
            * data (pandas.DataFrame): A numeric dataset in a pandas.DataFrame format.
            * excluded_axis (list, optional): A list of column names for the columns to be excluded from the scaling process. Defaults to `[]`.
            * scaler (str, optional): selects the scaling technique used as integers from `"0"` to `"8"` passed as strings, or the name of the scaling technique such as `"RawData (no scaling)"` or `"normalizer"`. Defaults to `"minmax"`.
            * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``1``.

        Returns:
            * tuple: (pandas.DataFrame,str) A scaled pandas.DataFrame Data and the name of the scaling technique used as string.
        """
        data = DataFrame(data)
        scaled_df = DataFrame(data)
        scaled_df = scaled_df.drop(excluded_axis, axis=1)
        columns_names_list = scaled_df.columns
        scaler = str(scaler)
        if scaler == "0" or scaler == "raw_data":
            scaler_name = "RawData (no scaling)"
            scaled_df = DataFrame()
            for column in data.columns:
                scaled_df[column] = data[column].astype("float")
                scaled_df = scaled_df.reset_index(drop=True)
            scaled_df = scaled_df.fillna(0)
            if verbose == 1:
                print(f"data was not scaled, returned: {scaler_name}")
            return scaled_df, scaler_name
        elif scaler == "1" or scaler == "minmax":
            scalerfunction = MinMaxScaler()
            scaler_name = "MinMaxscaler"
        elif scaler == "2" or scaler == "standard":
            scalerfunction = StandardScaler()
            scaler_name = "Standardscaler"
        elif scaler == "3" or scaler == "maxabs":
            scalerfunction = MaxAbsScaler()
            scaler_name = "MaxAbsScaler"
        elif scaler == "4" or scaler == "robust":
            scalerfunction = RobustScaler()
            scaler_name = "RobustScaler"
        elif scaler == "5" or scaler == "quantile_normal":
            scalerfunction = QuantileTransformer(output_distribution="normal")
            scaler_name = "QuantileTransformer using normal distribution"
        elif scaler == "6" or scaler == "quantile_uniform":
            scalerfunction = QuantileTransformer(output_distribution="uniform")
            scaler_name = "QuantileTransformer using uniform distribution"
        elif scaler == "7" or scaler == "power_transform":
            scalerfunction = PowerTransformer(method="yeo-johnson")
            scaler_name = "PowerTransformer using the yeo-johnson method"
        elif scaler == "8" or scaler == "normalizer":
            scalerfunction = Normalizer()
            scaler_name = "Normalizer"
        else:
            print("\nERROR: wrong data entry or wrong scaler type\ninput data returned")
            scaler_name = "Worning : No scaling (something went wrong)"
            return data, scaler_name
        scaled_df = scalerfunction.fit_transform(scaled_df)
        scaled_df = DataFrame(scaled_df, columns=columns_names_list)
        for i in excluded_axis:
            scaled_df[i] = data[i]
        scaled_df = scaled_df.fillna(0)
        if verbose == 1:
            print(f"data scaled with the {scaler_name}")
        return scaled_df, scaler_name

    @staticmethod
    def pca_decomposition(data, excluded=None, nb_components=None, verbose=1):
        """A static method for Principal Component Analysis.

        Args:
            data (DataFrame or numpy array): data to be decomposed by Principal Component Analysis.
            excluded (list, optional): list of column names to be excluded from the PCA decomposition. Defaults to `None`.
            nb_components (_type_, optional): the number of PCA components to produce. Defaults to `None`.
            verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``1``.

        Returns:
            DataFrame: A new dataframe with the pca components and the excluded columns as in the entry.
        """
        excluded = [] if excluded is None else excluded
        data = DataFrame(data)
        X = data.drop(excluded, axis=1)
        y = data[excluded]
        pca = PCA(n_components=nb_components)
        df = pca.fit_transform(X)
        df = DataFrame(df)
        df[excluded] = y
        if verbose == 1:
            print(
                f"\nData decomposed using PCA into {nb_components} components successfully.\n"
            )
            components_ratio = [
                "{:.2%}".format(i) for i in pca.explained_variance_ratio_
            ]
            print(f"The components ratio is :\n{components_ratio}\n")
        return df

    @staticmethod
    def one_hot_encoding(data, target="target", verbose=1):
        """A static method to convert a single column to a number of columns corresponding to the number of unique values in that columns by One Hot encoding.
        Example:
            >>> df
            index              Timestamp              Speed              driver               road              target
            0                  7                  65.2                  1                  secondary                  normal
            1                  8                  68.5                  1                  secondary                  normal
            2                  9                  73.6                  1                  secondary                  normal
            3                 10                  80.2                  1                  secondary                  agressif
            4                 11                  90.9                  1                  secondary                  agressif
            >>> print(df[target].unique())
            ['normal' 'agressif']
            >>> df_ohe = one_hot_encoding(df,target="target",verbose=0)
            >>> df_ohe
                    0    1
            0      0.0  1.0
            1      0.0  1.0
            2      0.0  1.0
            3      1.0  0.0
            4      1.0  0.0

        Args:
            * data (pandas.DataFrame): A data array in pandas.DataFrame format.
            * target (str, optional): The name of the target column that is going to be one hot encoded. Defaults to `"target"`.
            * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``1``.

        Returns:
            * pandas.DataFrame: the target column converted to binary format in a pandas.DataFrame with the number of columns corresponds to the unique values of the target column.
        """
        data = DataFrame(data)
        encoder = OneHotEncoder()
        try:
            if verbose == 1:
                print(f"One Hot Encoder target: {data[target].unique()}")
            encoded = encoder.fit_transform(
                data[target].values.reshape(-1, 1)
            ).toarray()
        except Exception:
            try:
                if verbose == 1:
                    print(f"One Hot Encoder target: {data.unique()}")
                encoded = encoder.fit_transform(data.values.reshape(-1, 1)).toarray()
            except Exception:
                raise KeyError(f"target name '{target}' is not available in data")
        if verbose == 1:
            print(f"example of the target after One Hot encoding : {encoded[0]}")
        df = DataFrame(encoded)
        return df


if __name__ == "__main__":
    from maaml.Datasets.UAH_dataset.time_series import UAHDatasetLoader

    raw = UAHDatasetLoader()
    preprocessor = DataPreprocessor(
        data=raw.data,
        droped_columns=["Timestamp (seconds)"],
        no_encoding_columns=None,
        no_scaling_columns=None,
        nb_pca_component=None,
        scaler=2,
        window_size=60,
        step=10,
        window_transformation=False,
        window_transformation_function=transposing,
        transformation_kwargs={"excluded": ["target"]},
        save_to=False,
        verbose=1,
    )
    print(f"\nthe raw dataset is: \n{preprocessor.raw_dataset}")
    print(f"\nthe dataset(after dropping columns) is\n{preprocessor.filtered_dataset}")
    print(f"the label encoded dataset: \n{preprocessor.numeric_dataset}")
    print(f"The used scaler is: {preprocessor.scaler_name}")
    print(f"\nthe scaled dataset is: \n{preprocessor.scaled_dataset}")
    print(f"\nthe dataset features are: \n{preprocessor.features}")
    print(f"\nthe dataset target column is: \n{preprocessor.target}")
    print(f"\nthe dataset one hot encoded target is: \n{preprocessor.target_ohe}")
    print(f"\nthe full preprocessed dataset is: \n{preprocessor.preprocessed_dataset}")
    print("\n ******* windowed data ******* \n")
    print(f"\nthe dataset windowed features are: \n{preprocessor.features_w}")
    print(f"\nthe dataset windowed target column is: \n{preprocessor.target_w}")
    print(
        f"\nthe dataset windowed one hot encoded target is: \n{preprocessor.target_ohe_w}"
    )
    print(
        f"\nthe full windowed preprocessed dataset is: \n{preprocessor.preprocessed_dataset_w}"
    )
    print(f"\npreprocessing info : {preprocessor.preprocessing_info}")
