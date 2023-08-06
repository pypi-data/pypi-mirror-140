from maaml.utils import DataFrame, save_csv, save_parquet, window_stepping, columns_mean
import time


class DataCleaner:
    """A class for data cleaning.

    Args:
    * data (pandas.DataFrame or array or numpy.array): A time series dataset.
    * merge_data (pandas.DataFrame or array or numpy.array, optional): A time series dataset to be merged with the data in the `data` parameter. Defaults to `None`.
    * window_size (int, optional): the size of the window in the case of window stepping the data, in case of `None` will not perform the window stepping. Defaults to `None`.
    * step (int, optional): The length of the step for window stepping,if `None` will not perform the window stepping, if smaller than `window_size` will result in overlapping windows, if equal to `window_size` performs standard window stepping, if bigger will skip some rows (not recommended). Defaults to `None`.
    * drop_duplicates (bool, optional): if `True` removes the duplicate values using the Timestamp column as refrence. Defaults to `True`.
    * window_transformation (bool, optional): in case of True applies the function in `window_transformation_function` parameter to the window. Defaults to `False`.
    * transformation_fn (function, optional): A function to be applied to the window, it takes the window dataframe as argument. Defaults to applying mean mean values on the columns with: `columns_mean`.
    * transformation_kwargs (dict,optional): A dictionary of keyword arguments (function arguments names and their values) specific to the function introduced in the transformation_fn, if not set will not pass any arguments to the function.Defaults to `None`.    * add_columns_dictionnary (dict, optional): A dictionnary of keys (column names) and values to be added to the array or the pandas.DataFrame, if set to `None` will skip adding data. Defaults to `None`.
    * save_to (str, optional): Can be `"csv"` or `"parquet"` or `None` if set to `"csv"` or `"parquet"` will save the dataset to the corresponding format in a newly created directory under the working directory, if set to `None` will not save the dataset. Defaults to `None`.
    * save_tag (str, optional): add the name tag of the file to be saved in the case of save_dataset is `True`. Defaults to `"dataset"`.
    * timestamp_column (str, optional): the name of the column that has the timpestamps in seconds of the time series data. Defaults to `"Timestamp (seconds)"`.
    * verbose (int, optional): An integer of the verbosity of the process can be ``0`` or ``1``. Defaults to ``0``.
    """

    def __init__(
        self,
        data,
        merge_data=None,
        window_size: int = None,
        step: int = None,
        drop_duplicates=True,
        window_transformation=False,
        window_transformation_function=columns_mean,
        transformation_kwargs=None,
        add_columns_dictionnary: dict = None,
        save_to=None,
        save_tag="dataset",
        timestamp_column="Timestamp (seconds)",
        verbose=0,
    ):
        """A constructor for DataCleaner class.

        Args:
        * data (pandas.DataFrame or array or numpy.array): A time series dataset.
        * merge_data (pandas.DataFrame or array or numpy.array, optional): A time series dataset to be merged with the data in the `data` parameter. Defaults to `None`.
        * window_size (int, optional): the size of the window in the case of window stepping the data, in case of `None` will not perform the window stepping. Defaults to `None`.
        * step (int, optional): The length of the step for window stepping,if `None` will not perform the window stepping, if smaller than `window_size` will result in overlapping windows, if equal to `window_size` performs standard window stepping, if bigger will skip some rows (not recommended). Defaults to `None`.
        * drop_duplicates (bool, optional): if `True` removes the duplicate values using the Timestamp column as reference. Defaults to `True`.
        * window_transformation (bool, optional): in case of True applies the function in `window_transformation_function` parameter to the window. Defaults to `False`.
        * transformation_fn (function, optional): A function to be applied to the window, it takes the window dataframe as argument. Defaults to applying mean mean values on the columns with: `columns_mean`.
        * transformation_kwargs (dict,optional): A dictionary of keyword arguments (function arguments names and their values) specific to the function introduced in the transformation_fn, if not set will not pass any arguments to the function.Defaults to `None`.        * add_columns_dictionnary (dict, optional): A dictionnary of keys (column names) and values to be added to the array or the pandas.DataFrame, if set to `None` will skip adding data. Defaults to `None`.
        * save_to (str, optional): Can be `"csv"` or `"parquet"` or `None` if set to `"csv"` or `"parquet"` will save the dataset to the corresponding format in a newly created directory under the working directory, if set to `None` will not save the dataset. Defaults to `None`.
        * save_tag (str, optional): add the name tag of the file to be saved in the case of save_dataset is `True`. Defaults to `"dataset"`.
        * timestamp_column (str, optional): the name of the column that has the timpestamps in seconds of the time series data. Defaults to `"Timestamp (seconds)"`.
        * verbose (int, optional): An integer of the verbosity of the process can be ``0`` or ``1``. Defaults to ``0``.
        """
        start_time = time.perf_counter()
        data = DataFrame(data)
        self.raw_data = data.copy(deep=True)
        if drop_duplicates is True:
            self.filtered_data = data.drop_duplicates(subset=[timestamp_column])
            if verbose == 1:
                print(
                    f"\nData filtered successfully, duplicates droped based on '{timestamp_column}' column."
                )
        else:
            self.filtered_data = data
            if verbose == 1:
                print(f"\nNo duplicates droped, filtered_data is raw_data.")
        if (window_size is None) and (step is None):
            self.windowed_data = self.filtered_data
            if verbose == 1:
                print(f"No window stepping,windowed_data is filtered_data.")
        else:
            self.windowed_data = window_stepping(
                self.filtered_data,
                window_size=window_size,
                step=step,
                window_transformation=window_transformation,
                transformation_fn=window_transformation_function,
                transformation_kwargs=transformation_kwargs,
                verbose=verbose,
            )
            self.windowed_data = self.windowed_data.dropna()
        if merge_data is not None:
            self.merged_data = self.dataframes_merging(
                self.windowed_data,
                merge_data,
                timestamp_column=timestamp_column,
                drop_duplicates=drop_duplicates,
                verbose=verbose,
            )
        else:
            self.merged_data = self.windowed_data
            if verbose == 1:
                print(f"No data merging,merged_data is windowed_data.")
        self.interpolated_data = self.data_interpolating(
            self.merged_data, timestamp_column=timestamp_column, verbose=verbose
        )
        self.dataset = self.removing_incomplete_raws(
            self.interpolated_data, verbose=verbose
        )
        if add_columns_dictionnary is not None:
            self.dataset = self.column_adding(
                self.dataset,
                add_columns_dictionnary=add_columns_dictionnary,
                verbose=verbose,
            )
        PATH = "cleaned_dataset"
        if save_to == "csv":
            save_csv(self.dataset, PATH, save_tag, verbose=verbose)
        elif save_to == "parquet":
            save_parquet(self.dataset, PATH, save_tag, verbose=verbose)
        self.exec_time = time.perf_counter() - start_time
        if verbose == 1:
            print(
                f"\n\033[1m========= DATA CLEANED SUCCESSFULLY [ ET: {self.exec_time:.2f} (s) ] =========\033[0m\n"
            )

    def __call__(self):
        """A method for the class instance call

        Returns:
            * pandas.DataFrame: The cleaned dataset.
        """
        return self.dataset

    @staticmethod
    def dataframes_merging(
        data=None,
        new_data=None,
        timestamp_column="Timestamp (seconds)",
        drop_duplicates=True,
        verbose=1,
    ):
        """A static method for merging two dataframes.

        Args:
            * data (pandas.DataFrame, optional): A time series dataframe. Defaults to `None`.
            * new_data (pandas.DataFrame or array or numpy.array, optional): A time series dataset to be merged with the data in the `data` parameter. Defaults to `None`.
            * timestamp_column (str, optional): The name of the timestamp column to be used as reference for the merge operation. Defaults to `"Timestamp (seconds)"`.
            * drop_duplicates (bool, optional): if `True` removes the duplicate values  in  both dataframes using the Timestamp column as reference before the merge operation. Defaults to `True`.
            * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``1``.

        Returns:
            * pandas.DataFrame: a pandas.Dataframe with the two orginal dataframes merged using `timestamp_column` as reference.
        """
        data = DataFrame(data)
        new_data = DataFrame(new_data)
        try:
            while data.dtypes[timestamp_column] != "int64":
                if verbose == 1:
                    print(
                        "\nWarning: data Timestamp type is: ",
                        data.dtypes[timestamp_column],
                        "\n",
                    )
                data = data.astype({timestamp_column: "int"})
                if verbose == 1:
                    print(
                        "data timestamp type changed to : ",
                        data.dtypes[timestamp_column],
                        "\n",
                    )
            while new_data.dtypes[timestamp_column] != "int64":
                if verbose == 1:
                    print(
                        "Warning: new_data Timestamp type is: ",
                        data.dtypes[timestamp_column],
                        "\n",
                    )
                new_data = new_data.astype({timestamp_column: "int"})
                if verbose == 1:
                    print(
                        "new_data timestamp type changed to : ",
                        new_data.dtypes[timestamp_column],
                        "\n",
                    )
            if drop_duplicates is True:
                data = data.drop_duplicates([timestamp_column])
                new_data = new_data.drop_duplicates([timestamp_column])
            data_merged = data.set_index(timestamp_column).join(
                new_data.set_index(timestamp_column)
            )
            data_merged = data_merged.reset_index()
            if verbose == 1:
                print(
                    f"\nShape of data before merge: {data.shape} | Shape of data to be merged: {new_data.shape} ."
                )
                print(
                    f"\033[1mShape of the merged data: {data_merged.shape} .\033[0m\n"
                )
                print("\033[1m", "******* DATA SUCCESSFULLY MERGED *******", "\033[0m")
        except Exception:
            raise ValueError(
                f"One empty data entry or more or {timestamp_column} exists in one dataframe and not the other."
            )
        return data_merged

    @staticmethod
    def data_interpolating(
        data=None, timestamp_column="Timestamp (seconds)", verbose=1
    ):
        """A static method for data interpolation.

        Args:
            * data (pandas.DataFrame, optional): A time series dataframe with missing values. Defaults to `None`.
            * timestamp_columns (str, optional): The name of the timestamp column for the time series data (to ignore this column in the interpolation). Defaults to `"Timestamp (seconds)"`.
            * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``1``.

        Returns:
            * pandas.DataFrame: A pandas.DataFrame with filled missing values.
        """
        data = DataFrame(data)
        try:
            if verbose == 1:
                print(
                    f"\n    State before interpolation    \nCOLUMNS                   NUMBER OF RAWS WITH MISSING DATA\n{data.isnull().sum()}\n"
                )
            if data.isnull().values.any() == True:
                if verbose == 1:
                    print("\n       Executing interpolation     \n")
                missing_values = data.drop(timestamp_column, axis=1)
                missing_values = missing_values.interpolate(method="cubic", limit=3)
                data_interpolated = data.copy(deep=True)
                data_interpolated[missing_values.columns] = missing_values
                if verbose == 1:
                    print(
                        f"\n    State after interpolation    \nCOLUMNS                   NUMBER OF RAWS WITH MISSING DATA\n{data_interpolated.isnull().sum()}\n"
                    )
            else:
                data_interpolated = data
                if verbose == 1:
                    print("\n   Interpolation not needed    \n")
        except Exception:
            raise ValueError("Empty data entry")
        return data_interpolated

    @staticmethod
    def removing_incomplete_raws(data=None, verbose=1):
        """A static method for removing all Nan or Na values.

        Args:
            * data (pandas.DataFrame, optional): A dataframe. Defaults to `None`.
            * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``1``.

        Returns:
            * pandas.DataFrame: a dataframe with no missing or Nan/ Na/ None values.
        """
        data = DataFrame(data)
        try:
            if verbose == 1:
                print(
                    f"\n    Data count before removing any rows :     \n{data.count()}"
                )
                print(
                    "\nIs there any missing data values? :",
                    "\033[1m",
                    data.isnull().values.any(),
                    "\033[0m",
                )
            data = data.dropna()
            data = data.reset_index(drop=True)
            if verbose == 1:
                print(f"\n  Final Data count :     \n{data.count()}")
                print(
                    "\nis there any missing data values? :",
                    "\033[1m",
                    data.isnull().values.any(),
                    "\033[0m",
                )
        except Exception:
            raise ValueError("Empty data entry.")
        return data

    @staticmethod
    def column_adding(
        data,
        add_columns_dictionnary: dict = None,
        column_name: str = None,
        value: str = None,
        verbose=0,
    ):
        """A static method for adding columns into a pandas.DataFrame.

        Args:
            * data (pandas.DataFrame): A dataframe. Defaults to `None`.
            * add_columns_dictionnary (dict, optional): A dictionnary of keys (column names) and corresponding values to be added, if set to `None` will check `column_name` and `value` if one of them is `None` will skip adding data. Defaults to `None`.
            * column_name (str, optional): the name of the new column. Defaults to `None`.
            * value (Any, optional): The value of the new column. Defaults to `None`.
            * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``0``.

        Returns:
            [type]: [description]
        """
        if add_columns_dictionnary is None:
            if column_name is not None and value is not None:
                data[column_name] = value
            else:
                data = data
                if verbose == 1:
                    print("\n    No columns added    \n")
        else:
            for key in add_columns_dictionnary:
                try:
                    data[key] = add_columns_dictionnary[key]
                    if verbose == 1:
                        print(f"\nThe '{key}' column was added successfully   \n")
                except ValueError:
                    print(
                        f"\nAbort column adding operation : The '{key}' column length is {len(add_columns_dictionnary[key])}, while the data length {len(data)}\n"
                    )
                    break
        return data


if __name__ == "__main__":
    DATA_DIR_PATH = "/run/media/najem/34b207a8-0f0c-4398-bba2-f31339727706/home/stock/The_stock/dev & datasets/PhD/datasets/UAH-DRIVESET-v1/"
    my_dict = {
        "Timestamp (seconds)": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 4],
        "speed": [40, 45, 60, 62, 70, 75, 80, None, 72, 70, 80],
        "loc": [3, 4, 7, 10, None, 15, 17, 20, 24, 27, 5],
        "driver": ["D1", "D1", "D1", "D1", "D2", "D4", None, "D2", "D1", "D5", "D6"],
        "target": [
            "normal",
            "normal",
            "normal",
            "agressif",
            "agressif",
            "drowsy",
            "normal",
            "normal",
            "normal",
            "drowsy",
            "normal",
        ],
    }
    data = my_dict
    cleaning = DataCleaner(
        data,
        merge_data={
            "Timestamp (seconds)": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 4],
            "axis": [12, 4, 5, 7, 5, 8, 2, 5, 4, 6, 8],
        },
        window_size=5,
        step=2,
        window_transformation=False,
        drop_duplicates=True,
        add_columns_dictionnary={"axis_origin": [12, 4, 5, 7, 5, 8, 2, 5, 4]},
        save_to=None,
        verbose=1,
    )
    print("raw data:\n", cleaning.raw_data)
    print("filtered data:\n", cleaning.filtered_data)
    print("windowed data:\n", cleaning.windowed_data)
    print("merged data:\n", cleaning.merged_data)
    print("interpolated data:\n", cleaning.interpolated_data)
    print("cleaned data:\n", cleaning.dataset)
    test_dict = {
        "Timestamp (seconds)": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 4],
        "speed": [40, 45, 60, 62, 70, 75, 80, 0, 72, 70, 80],
        "loc": [3, 4, 7, 10, 0, 15, 17, 20, 24, 27, 5],
    }
    test = window_stepping(test_dict, 5, 2, window_transformation=True, verbose=1)
    print(test)
