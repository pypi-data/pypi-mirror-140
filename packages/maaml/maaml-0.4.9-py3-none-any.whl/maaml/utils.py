import os
import pandas as pd
import time
from math import sqrt

mean = lambda data: float(sum(data) / len(data))
variance = lambda data: sum([x ** 2 for x in [i - mean(data) for i in data]]) / float(
    len(data)
)
std_dev = lambda data: sqrt(variance(data))


class DataFrame(pd.DataFrame):
    """A class to create a DataFrame.

    Args:
        * pandas.DataFrame (object): A pandas dataframe.
    """

    def __init__(self, *args, **kwargs):
        """A constructor for DataFrame class."""
        super().__init__(*args, **kwargs)


class DataReader:
    """A class for reading data in the form of dataframes from a file. includes a `path` attribute and `data` attribute and a `__call__ ` method for calling an instance of the class to return the `data` attribute.

    Args:
        * path (str): The data file name in the working directory or the data file path with the file name.
        * header (int, optional):  The specification of the technique used to define the columns names, if needed for the file format,should be `None` in case of no columns names in the file, `0` in case that first row is the header. Defaults to `None`.
        * delimiter (str, optional): A string for the type of separation used in the file, if needed for the file format. Defaults to `" "`.
        * read_from (str,optinoal): The format of the read data such as `"csv"` or `"parquet"`, if set to `None` DataReader will try to guess the format. Defaults to `None`.
        * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``0``.
    """

    def __init__(
        self, path, header=None, delimiter=" ", read_from: str = None, verbose=0
    ):
        """A constuctor for DataReader class.

        Args:
        * path (str): The data file name in the working directory or the data file path with the file name.
        * header (int, optional):  The specification of the technique used to define the columns names: `None` in case of no columns names in the file, `0` in case that first row is the header. Defaults to `None`.
        * delimiter (str, optional): A string for the type of separation used in the csv file. Defaults to `" "`.
        * read_from (str,optinoal): The format of the read data such as `"csv"` or `"parquet"`, if set to `None` DataReader will try to guess the format. Defaults to `None`.
        * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``0``.
        """
        self.path = str(path)
        if path.endswith(".csv") or read_from == "csv":
            self.data = read_csv(
                path, header=header, delimiter=delimiter, verbose=verbose
            )
        elif path.endswith(".parquet") or read_from == "parquet":
            self.data = read_parquet(path, verbose=verbose)
        else:
            try:
                self.data = read_csv(
                    path, header=header, delimiter=delimiter, verbose=0
                )
                if verbose == 1:
                    print(f"\033[1mReading file from:\n{path} \033[0m\n")
            except Exception:
                if read_from is not None:
                    print(
                        f"please be specific about the data_format,your data_format '{read_from}' is not supported"
                    )
                else:
                    print("please set the data_format")

    def __call__(self):
        """A method for the class instance call

        Returns:
            * pandas.DataFrame: The read dataset from the file.
        """
        return self.data


def save_csv(df, path, name, verbose=0, prompt=None):
    """saves a csv file from pandas DataFrame to the given path with the given name,
    if the entry is not a pandas DataFrame, it gets transformed to a pandas
    DataFrame before saving it

    Args:
        * df (pandas.DataFrame or array or numpy.array): A pandas.DataFrame or an array or a numpy.array
        * path (str): A string of the path where the file is going to be saved
        * name (str): A string of the name of the saved file with or without the .csv extention
        * verbose (int, optional): An integer of the verbosity of the function can be ``0`` or ``1``. Defaults to ``0``.
        * prompt (str, optional): A string of a custom prompt that is going to be displayed instead of the default generated prompt in case of verbosity set to ``1``. Defaults to ``None``.
    """
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    if not name.endswith(".csv"):
        name = name + ".csv"
    if not os.path.exists(path):
        os.makedirs(path)
    full_path = os.path.join(path, name)
    df.to_csv(full_path, index=False)
    if verbose > 0:
        if prompt is None:
            abs_path = os.path.join(os.getcwd(), path)
            print(
                f"\n\033[1mThe file {name} was saved in the path :\n{abs_path} \033[0m\n"
            )
        else:
            print(prompt)


def save_parquet(df, path, name, verbose=0, prompt=None):
    """saves a parquet file from pandas DataFrame to the given path with the given name,
    if the entry is not a pandas DataFrame, it gets transformed to a pandas
    DataFrame before saving it

    Args:
        * df (pandas.DataFrame or array or numpy.array): A pandas.DataFrame or an array or a numpy.array
        * path (str): A string of the path where the file is going to be saved
        * name (str): A string of the name of the saved file with or without the .parquet extention
        * verbose (int, optional): An integer of the verbosity of the function can be ``0`` or ``1``. Defaults to ``0``.
        * prompt (str, optional): A string of a custom prompt that is going to be displayed instead of the default generated prompt in case of verbosity set to ``1``. Defaults to ``None``.
    """
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    if not name.endswith(".parquet"):
        name = name + ".parquet"
    if not os.path.exists(path):
        os.makedirs(path)
    full_path = os.path.join(path, name)
    df.to_parquet(full_path, index=False)
    if verbose > 0:
        if prompt is None:
            abs_path = os.path.join(os.getcwd(), path)
            print(
                f"\n\033[1mThe file {name} was saved in the path :\n{abs_path} \033[0m\n"
            )
        else:
            print(prompt)


def read_csv(path, delimiter=" ", header=None, verbose=0, prompt=None):
    """A function to read a csv file and return a pandas dataframe.

    Args:
        * path (str): The data file name in the working directory or the data file path with the file name.
        * delimiter (str, optional): A string for the type of separation used in the csv file. Defaults to ``" "``.
        * header (int, optional): The specification of the technique used to define the columns names: ``None`` in case of no columns names in the file, ``0`` in case that first row is the header. Defaults to ``None``.
        * verbose (int, optional): An integer of the verbosity of the function can be ``0`` or ``1``. Defaults to ``0``.
        * prompt (str, optional): A message in the case of verbose is ``1``, if not specified another default message will be displayed. Defaults to ``None``.

    Returns:
        * pandas.DataFrame: A pandas dataframe of the read file.
    """
    try:
        df_csv = pd.read_table(path, header=header, delimiter=delimiter)
    except FileNotFoundError:
        path = path + ".csv"
        df_csv = pd.read_table(path, header=header, delimiter=delimiter)
    if verbose > 0:
        if prompt is None:
            print(f"\n\033[1mLoading dataframe from csv file in:\n{path} \033[0m\n")
        else:
            print(prompt)
    return df_csv


def read_parquet(path, verbose=0, prompt=None):
    """A function to read a parquet file and return a pandas dataframe.

    Args:
        * path (str): The data file name in the working directory or the data file path with the file name.
        * delimiter (str, optional): A string for the type of separation used in the parquet file. Defaults to ``" "``.
        * verbose (int, optional): An integer of the verbosity of the function can be ``0`` or ``1``. Defaults to ``0``.
        * prompt (str, optional): A message in the case of verbose is ``1``, if not specified another default message will be displayed. Defaults to ``None``.

    Returns:
        * pandas.DataFrame: A pandas dataframe of the read file.
    """
    try:
        df_parquet = pd.read_parquet(path)
    except FileNotFoundError:
        path = path + "parquet"
        df_parquet = pd.read_parquet(path)
    if verbose > 0:
        if prompt is None:
            print(f"\n\033[1mLoading dataframe from parquet file in:\n{path} \033[0m\n")
        else:
            print(prompt)
    return df_parquet


def dict_transpose(dictionary):
    """A function that transposes a dictionary,
    it simply uses the first key and it's values as the new keys and then maps the rest of the keys and their values to the newly created keys in the same order of apperance.

    Args:
        * dictionary (dict): A python dictionary

    Returns:
        * dict: A transposed python dictionary

    Example:
        >>> d = {
            "classifier": ["SVM","LR","MLP"],
            "scaler": ["Standard", "Standard", "Standard"],
            "exec time": ["75.88(s)", "4.78(s)", "94.89(s)"],
            "accuracy": ["78.5%","53.6%","88.6%"],
            "F1": ["78.6%","53.0%","88.6%"],
            }
        >>> d_transposed = dict_transpose(d)
        >>> d_transposed
            {
            "classifier": ["scaler","exec time","accuracy","F1"],
            "SVM": ["Standard","75.88(s)","78.5%","78.6%"],
            "LR": ["Standard","4.78(s)","53.6%","53.0%"],
            "MLP": ["Standard","94.89(s)","88.6%","88.6%"],
            }
    """
    keys_list = list(dictionary)
    values_list = list(dictionary.values())
    new_dict = {keys_list[0]: keys_list[1:]}
    new_keys = values_list[0]
    for key in new_keys:
        new_dict[key] = []
    for values in values_list[1:]:
        for key, v in zip(new_keys, values):
            new_dict[key].append(v)
    return new_dict


class FileScraper:
    """A class for file scraping from a specific directory. includes ``path_list`` attribute representing the paths of the searched files in a list of strings format.
    ``found_files_count`` attribute represnting the number of files found.
    `all_files` attribute represnting the paths of all existing files in a list of strings format available in the given path directory.
    ``all_files_count`` attribute representing the number of all existing files available in the given path directory.
    `time` attribute representing the execution time of the search.
    A `__call__ ` method for calling an instance of the class to return the `path_list` attribute.


    Args:
        * path (str): The path to the search directory.
        * search_list (list): List of strings representing the searched files.
        * verbose (int, optional): An integer of the verbosity of the function can be ``0`` or ``1``. Defaults to ``0``.
    """

    def __init__(self, path, search_list, verbose=0) -> None:
        """The constructor of the FileScraper class.

        Args:
            * path (str): The path to the search directory.
            * search_list (list): List of strings representing the searched files.
            * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1`` or ``2`` or ``3``. Defaults to ``0``.
        """
        self.verbose = verbose
        start_time = time.perf_counter()
        self.parent_path = path
        self.search_list = set(search_list)
        self.searched_list = search_list.copy()
        self.file_scraping(self.parent_path, self.search_list)
        self.found_files_count = len(self.path_list)
        self.all_files_count = len(self.all_files)
        end_time = time.perf_counter()
        self.time = f"{end_time-start_time} (s)"
        if self.verbose == 1:
            print(f"Finished searching in {self.time}")
            print(
                f"{self.found_files_count} matching files found from total of {self.all_files_count} existant files"
            )
        if len(self.searched_list):
            print(f"These elements are not found: {self.searched_list}\n")
        else:
            if self.verbose == 1:
                print("*******All searched elements were found successfully*******\n")

    def __call__(self):
        """A method for the class instance call

        Returns:
            * list: list of strings representing the paths of the searched files.
        """
        return self.path_list

    def file_scraping(self, path, search_list):
        """A class method that searches

        Args:
            * path (str): The path to the search directory.

        Returns:
            list: list of strings representing the paths of the searched files.
        """
        files = []
        for text in os.listdir(path):
            if os.path.isdir(os.path.join(path, text)):
                if self.verbose == 3:
                    print(f"Changing directory to subdirectory: '{text}'")
                dir = os.path.join(path, text)
                localfiles = self.file_scraping(dir, search_list)
                if self.verbose == 3:
                    if localfiles != []:
                        print(f"'{text}' files :{localfiles}")
                if localfiles == []:
                    localfiles, dir = files, path
                    if self.verbose == 3:
                        if localfiles == []:
                            print(f"No files found in the '{text}' directory")
                        else:
                            print(f"Changing directory to main directory:")
                            print(f"'{dir}'\nfiles :{localfiles}")
                for file in localfiles:
                    file_path = os.path.join(dir, file)
                    try:
                        if file not in self.all_files:
                            self.all_files.append(file_path)
                    except AttributeError:
                        self.all_files = [file_path]
                    for picked_file in search_list:
                        if file == picked_file:
                            if picked_file in self.searched_list:
                                self.searched_list.remove(picked_file)
                            try:
                                if file_path not in self.path_list:
                                    self.path_list.append(file_path)
                                    if self.verbose == 2:
                                        print(f"file '{file}' found in: \n{dir}")
                                        print(
                                            "**File path added to the path_list successfully**\n"
                                        )
                            except AttributeError:
                                self.path_list = [file_path]
                                if self.verbose == 2:
                                    print(f"file '{file}' found in: \n{dir}")
                                    print(
                                        "**Initalization of the path_list with the file path is successful**\n"
                                    )

            elif os.path.isfile(os.path.join(path, text)):
                files.append(text)
        return files


def pattern_search(pattern, local_set, error_message, global_set=None):
    """A function to collect phrases starting from a string pattern.

    Args:
        * pattern (str): A sylable or a part of a word that we want to find.
        * local_set (set): a set or list of complete and correct words that the pattern could be in.
        * error_message (str): a message to print with the ValueError raised in case pattern is not found.
        * global_set (set): a set or a list of phrases that we want to find the word that match the pattern in. If set to `None`, the search is condacted only in the local_set. Defaults to `None`.

    Returns:
        * set: a set of the phrases that contain the word matching the entry pattern.
    """
    matching_result_set = set()
    for word in local_set:
        if pattern in word:
            if global_set:
                for element in global_set:
                    if word in element:
                        matching_result_set.add(element)
            else:
                matching_result_set.add(word)
    if len(matching_result_set):
        return matching_result_set
    else:
        raise ValueError(error_message)


def columns_mean(df):
    """A function to apply mean on a dataframe columns.

    Args:
        - df (pandas.Dataframe): a dtaframe to apply the mean to all it's columns.

    Returns:
        - pandas.DataFrame: A dataframe with the mean of every column.
    """
    return df.apply(lambda x: sum(x) / len(x))


def window_stepping(
    data=None,
    window_size: int = None,
    step: int = None,
    window_transformation: bool = False,
    transformation_fn=columns_mean,
    transformation_kwargs: dict = None,
    verbose: int = 1,
):
    """A function for window stepping a time series data.

    Args:
        * data (pandas.DataFrame, optional): A data array in pandas.DataFrame format. Defaults to `None`.
        * window_size (int, optional): the size of the window, in case of `None` will not perform the window stepping and will raise ValueError. Defaults to `None`.
        * step (int, optional): The length of the step,if `None` will not perform the window stepping and will raise ValueError, if smaller than `window_size` will result in overlapping windows, if equal to `window_size` performs standard window stepping, if bigger will skip some rows (not recommended). Defaults to `None`.
        * window_transformation (bool, optional): in case of True applies the function in `window_transformation_function` parameter to the window. Defaults to `False`.
        * transformation_fn (function, optional): A function to be applied to the window, it takes the window dataframe as argument. Defaults to applying mean mean values on the columns with: `columns_mean`.
        * transformation_kwargs (dict,optional): A dictionary of keyword arguments (function arguments names and their values) specific to the function introduced in the transformation_fn, if not set will not pass any arguments to the function.Defaults to `None`.
        * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``1``.

    Returns:
        * pandas.DataFrame: A window stepped data in case the window was bigger than 0 or the entry dataframe in case window_size is equal to 0.
    """
    data = DataFrame(data)
    if len(data) != 0:
        if (window_size is not None) and (step is not None):
            if window_size == 0 or step == 0:
                raise ValueError(
                    "Window stepping is not possible,one or both of window_size and step is set to 0."
                )
            elif step >= len(data) or window_size >= len(data):
                raise ValueError(
                    "Window stepping is not possible,The length of one or both window_size and step parameters is the same or bigger than the data length."
                )
            else:
                final_data = DataFrame()
                for i in range(0, len(data) - 1, step):
                    window_segment = data[i : i + window_size]
                    if window_transformation is True:
                        try:
                            transformation_kwargs = (
                                {}
                                if transformation_kwargs is None
                                else transformation_kwargs
                            )
                            window_segment = transformation_fn(
                                window_segment, **transformation_kwargs
                            )
                        except TypeError:
                            raise TypeError(
                                "\033[1mCan not apply window_transformation function, the function does not conform with the data types.\033[0m"
                            )
                    final_data = final_data.append(window_segment, ignore_index=True)
                if verbose == 1:
                    if window_transformation is True:
                        print("\n\033[1mWindow transformation applied.\033[0m")
                    else:
                        print(
                            f"\nWindow stepping applied with window size: {window_size} and step : {step} ."
                        )
        else:
            raise ValueError(
                "Window stepping is not possible,one or both of window_size and step is not set."
            )
    else:
        raise ValueError("Empty data entry")
    return final_data


def transposing(data, excluded=None, verbose=0):
    """A function to transpose a dataframe.

    Args:
        - data (pandas.DataFrame): A dataFrame to be transposed.
        - excluded (list, optional): A list of columns names to be excluded from the transpose operation. Defaults to `None`.
        - verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``1``.

    Raises:
        - KeyError: if one of the excluded list does not exist in the data columns names.
        - ValueError: if the entry data is not a dataframe and cannot be transformed into dataframe.

    Returns:
        - pandas.DataFrame: A transposed dataframe.
    """
    data = DataFrame(data).reset_index(drop=True)
    excluded = [] if excluded is None else excluded
    if excluded != []:
        try:
            saved = data[excluded]
        except KeyError:
            raise KeyError("One column name or more in excluded does not exist in data")
        data = data.drop(excluded, axis=1).T
        if len(saved) >= len(data):
            data[excluded] = saved.loc[: len(data) - 1].values
        else:
            print(
                "The excluded columns are smaller than the transposed data..skipping adding them."
            )
        if verbose == 1:
            print(f"These columns are chosen to not be transposed:\n{excluded}")
    elif excluded == []:
        data = data.T
        if verbose == 1:
            print("Transposing all columns.")
    else:
        raise ValueError("Data is not acceptable format.")
    return data


if __name__ == "__main__":
    DATA_DIR_PATH = "/run/media/najem/34b207a8-0f0c-4398-bba2-f31339727706/home/stock/The_stock/dev & datasets/PhD/datasets/UAH-DRIVESET-v1"
    # 'RAW_ACCELEROMETERS.txt' "RAW_GPS.txt",
    file_list = FileScraper(
        DATA_DIR_PATH,
        search_list=["RAW_ACCELEROMETERS.txt", "RAW_GPS.txt", "try"],
        verbose=0,
    )
    print(file_list())
