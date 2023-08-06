from maaml.utils import (
    read_parquet,
    save_csv,
    FileScraper,
    pattern_search,
    read_csv,
    save_parquet,
    DataFrame,
)
from maaml.cleaning import DataCleaner
import pkg_resources


class UahDatasetPathFinder:
    """A class for generating a path for a specific file in the UahDataset. includes an attribute `file_path` and a method `numeric_to_string_from_list` for converting a nemeric value to the a corresponding indexed string from a list and a `__call__ ` method for calling an instance of the class to return the `file_path` attribute.

        Args:
        * dataset_dir (str): The path to the parent directory of the UahDataset.
        * driver (str or int): The number of the driver, can be an integer from `1` to `6` or a string that ends with integer in the same range such as `"driver1"` or `"D6"`.
        * state (str or int): The state of the driving session, can be an integer from `1` to `3` or a string such as `"normal"`,`"aggressive"` or `"drowsy"` not case sensitive.
        * road (str or int): The type of road in the driving session, can be an integer from `1` to `2` or a string such as `"motorway"` or `"secondary"` not case sensitive.
        * data_type (str or int): The type of data or the file of data chosen, can be an integer from 1 to 9 or a string such as `"gps"` or `"accelerometer"` not case sensitive.
        * standard (bool, optional): if `True` gives you the first session and if `False` gives the second session, of course for both cases it depends on the availability of the data. Defaults to `True`.
        * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``0``.

    Raises:
        * ValueError: In the case of wrong argement type or entry, with a description for the reason.
    """

    SENSOR_FILES = [
        "RAW_GPS.txt",
        "RAW_ACCELEROMETERS.txt",
        "PROC_LANE_DETECTION.txt",
        "PROC_VEHICLE_DETECTION.txt",
        "PROC_OPENSTREETMAP_DATA.txt",
        "EVENTS_LIST_LANE_CHANGES.txt",
        "EVENTS_INERTIAL.txt",
        "SEMANTIC_FINAL.txt",
        "SEMANTIC_ONLINE.txt",
    ]
    STATES = ["NORMAL", "AGGRESSIVE", "DROWSY"]
    ROADS = ["MOTORWAY", "SECONDARY"]

    def __init__(
        self, dataset_dir, driver, state, road, data_type, standard=True, verbose=0
    ):
        """A constructor for the UahDatasetPathFinder class.

            Args:
            * dataset_dir (str): The path to the parent directory of the UahDataset.
            * driver (str or int): The number of the driver, can be an integer from `1` to `6` or a string that ends with integer in the same range such as `"driver1"` or `"D6"`.
            * state (str or int): The state of the driving session, can be an integer from `1` to `3` or a string such as `"normal"`,`"aggressive"` or `"drowsy"` not case sensitive.
            * road (str or int): The type of road in the driving session, can be an integer from `1` to `2` or a string such as `"motorway"` or `"secondary"` not case sensitive.
            * data_type (str or int): The type of data or the file of data chosen, can be an integer from 1 to 9 or a string such as `"gps"` or `"accelerometer"` not case sensitive.
            * standard (bool, optional): if `True` gives you the first session and if `False` gives the second session, of course for both cases it depends on the availability of the data. Defaults to `True`.
            * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1`` or ``2``. Defaults to ``0``.

        Raises:
            * ValueError: In the case of wrong argement type or entry, with a description for the reason.
        """
        file_error_msg = (
            "Please give a correct data_type from the files available for the dataset."
        )
        numeric_file_error_msg = (
            "Please give the correct number of the file, only 9 file available."
        )
        data_type = self.numeric_to_string_from_list(
            data_type, self.SENSOR_FILES, numeric_file_error_msg
        ).replace(".txt", "")
        file_name = pattern_search(data_type.upper(), self.SENSOR_FILES, file_error_msg)
        if len(file_name) > 1:
            raise ValueError(
                f"There is more than one data_type with that entry:\n{file_name}\nplease be more specific."
            )
        else:
            for file in file_name:
                self.file = file
                if verbose == 1:
                    print(
                        f"Searching '{file}' file in all directories and sub_directories.. "
                    )

            scraper_verbose = 1 if verbose > 1 else verbose
            self.path_list = set(
                FileScraper(dataset_dir, file_name, verbose=scraper_verbose).path_list,
            )
            driver = (
                driver
                if isinstance(driver, int) or driver.isnumeric()
                else int(driver[-1])
            )
            driver_error_msg = (
                "Please give a correct driver number, only 6 drivers available."
            )
            driver_name = f"D{driver}"
            self.driver = driver_name
            driver_paths = pattern_search(driver_name, self.path_list, driver_error_msg)
            if verbose == 2:
                print(
                    f"\033[1mdriver {driver_name} has {len(driver_paths)} diffrent paths\033[0m"
                )
            numeric_state_error_msg = (
                "Please give the correct driving state number, only 3 states available."
            )
            state = self.numeric_to_string_from_list(
                state, self.STATES, error_msg=numeric_state_error_msg
            )
            state_error_msg = f"\nPlease give driving state number or give the correct driving state from:\n{self.STATES}"
            self.state = pattern_search(
                state.upper(), self.STATES, state_error_msg
            ).pop()
            state_paths = pattern_search(self.state, driver_paths, state_error_msg)
            numeric_road_error_msg = (
                "Please give the correct road number, only 2 roads available."
            )
            road = self.numeric_to_string_from_list(
                road, self.ROADS, numeric_road_error_msg
            )
            road_error_msg = f"\nPlease give road number or give the correct road name from:\n{self.ROADS}"
            self.road = pattern_search(road.upper(), self.ROADS, road_error_msg).pop()
            road_paths = pattern_search(self.road, state_paths, road_error_msg)
            road_paths = list(road_paths)
            if len(road_paths) > 1 and verbose == 2:
                print(
                    f"\nThere is more than one path for this case,the selection depended on the standard parameter."
                )
            if standard:
                try:
                    self.file_path = road_paths[0]
                except IndexError:
                    raise ValueError(
                        "Driver 6 does not have data for state: AGGRESSIVE and road: SECONDARY ."
                    )
            elif not standard:
                try:
                    self.file_path = road_paths[1]
                except IndexError:
                    raise ValueError("Only standard file available for this case.")
            if verbose == 2:
                print(f"\nThe file path is:\n\033[1m'{self.file_path}'\033[0m\n")

    def __call__(self):
        """A method for the class instance call

        Returns:
            * str: The file path.
        """
        return self.file_path

    def numeric_to_string_from_list(self, element, element_list, error_msg):
        """A method for checking if an element is an integer or numeric to return a string from a list matching it's index.

        Args:
            * element (int or str): An element to be checked if it is numeric.
            * element_list (set or list): A list to have matching strings for the numeric element.
            * error_msg (str): An error message to be displayed when a ValueError is raised.

        Raises:
            * ValueError: if the numeric element is not in the range of the element_list.

        Returns:
            * str: The string matching the index of the numeric elemnt or the entry element if the element is not a numeric value.
        """
        if isinstance(element, int) or element.isnumeric():
            if 0 < int(element) < len(element_list) + 1:
                element = element_list[int(element) - 1]
                return element
            else:
                raise ValueError(error_msg)
        return element


class UahDatasetReader(UahDatasetPathFinder):
    """A class for loading a UahDataset file into a dataframe, includes a dictionary attribute of the `files_column_names` and a `data` attribute, a `__call__ ` method for calling an instance of the class to return the `data` attribute.

    Args:
        * UahDatasetPathFinder (object): A class object for finding the UahDataset path.
        * parent_path (str): The path to the parent directory of the UahDataset.
        * driver_id (str or int): The number of the driver, can be an integer from `1` to `6` or a string that ends with integer in the same range such as `"driver1"` or `"D6"`.
        * state_id (str or int): The state of the driving session, can be an integer from `1` to `3` or a string such as `"normal"`,`"aggressive"` or `"drowsy"` not case sensitive.
        * road_id (str or int): The type of road in the driving session, can be an integer from `1` to `2` or a string such as `"motorway"` or `"secondary"` not case sensitive.
        * data_type_id (str or int): The type of data or the file of data chosen, can be an integer from 1 to 9 or a string such as `"gps"` or `"accelerometer"` not case sensitive.
        * standard (bool, optional): if `True` gives you the first session and if `False` gives the second session, of course for both cases it depends on the availability of the data. Defaults to `True`.
        * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``0``.
    """

    files_column_names = {
        "RAW_GPS.txt": [
            "Timestamp (seconds)",
            "Speed (km/h)",
            "Latitude coordinate (degrees)",
            "Longitude coordinate (degrees)",
            "Altitude (meters)",
            "Vertical accuracy (degrees)",
            "Horizontal accuracy (degrees)",
            "Course (degrees)",
            "Difcourse: course variation (degrees)",
        ],
        "RAW_ACCELEROMETERS.txt": [
            "Timestamp (seconds)",
            "Boolean of system activated (1 if >50km/h)",
            "Acceleration in X (Gs)",
            "Acceleration in Y (Gs)",
            "Acceleration in Z (Gs)",
            "Acceleration in X filtered by KF (Gs)",
            "Acceleration in Y filtered by KF (Gs)",
            "Acceleration in Z filtered by KF (Gs)",
            "Roll (degrees)",
            "Pitch (degrees)",
            "Yaw (degrees)",
        ],
        "PROC_LANE_DETECTION.txt": [
            "Timestamp (seconds)",
            "X: car position relative to lane center (meters)",
            "Phi: car angle relative to lane curvature (degrees)",
            "W: road width (meters)",
            "State of the lane det. algorithm [-1=calibrating,0=initializing, 1=undetected, 2=detected/running]",
        ],
        "PROC_VEHICLE_DETECTION.txt": [
            "Timestamp (seconds)",
            "Distance to ahead vehicle in current lane (meters) [value -1 means no car is detected in front]",
            "Time of impact to ahead vehicle (seconds) [distance related to own speed]",
            "Number of detected vehicles in this frame (traffic)",
            "GPS speed (km/h) [same as in RAW GPS]",
        ],
        "PROC_OPENSTREETMAP_DATA.txt": [
            "Timestamp (seconds)",
            "Maximum allowed speed of current road (km/h)",
            "Reliability of obtained maxspeed (0=unknown,1=reliable, 2=used previously obtained maxspeed,3=estimated by type of road)",
            "Type of road (motorway, trunk, secondary...)",
            "Number of lanes in current road",
            "Estimated current lane (1=right lane, 2=first left lane, 3=second left lane, etc) [experimental]",
            "GPS Latitude used to query OSM (degrees)",
            "GPS Longitude used to query OSM (degrees)",
            "OSM delay to answer query (seconds)",
            "GPS speed (km/h) [same as in RAW GPS]",
        ],
        "EVENTS_LIST_LANE_CHANGES.txt": [
            "Timestamp (seconds)",
            "Type [+ indicates right and - left, 1 indicates normal lane change and 2 slow lane change]",
            "GPS Latitude of the event (degrees)",
            "GPS Longitude of the event (degrees)",
            "Duration of the lane change (seconds) [measured since the car position is near the lane marks]",
            "Time threshold to consider irregular change (secs.) [slow if change duration is over this threshold and fast if duration is lower than threshold/3]",
        ],
        "EVENTS_INERTIAL.txt": [
            "Timestamp (seconds)",
            "Type (1=braking, 2=turning, 3=acceleration)",
            "Level (1=low, 2=medium, 3=high)",
            "GPS Latitude of the event",
            "GPS Longitude of the event ",
            "Date of the event in YYYYMMDDhhmmss format",
        ],
        "SEMANTIC_FINAL.txt": [
            "Hour of route start",
            "Minute of route start",
            "Second of route start",
            "Average speed during trip (km/h)",
            "Maximum achieved speed during route (km/h)",
            "Lanex score (internal value, related to lane drifting)",
            "Driving time (in minutes)",
            "Hour of route end",
            "Minute of route end",
            "Second of route end",
            "Trip distance (km)",
            "ScoreLongDist	(internal value, Score accelerations)",
            "ScoreTranDist	(internal value, Score turnings)",
            "ScoreSpeedDist (internal value, Score brakings)",
            "ScoreGlobal (internal value, old score that is not used anymore)",
            "Alerts Long (internal value)",
            "Alerts Late (internal value)",
            "Alerts Lanex (internal value)",
            "Number of vehicle stops during route (experimental, related to fuel efficiency estimation)",
            "Speed variability (experimental, related to fuel efficiency estimation)",
            "Acceleration noise (experimental, related to fuel efficiency estimation)",
            "Kinetic energy (experimental, related to fuel efficiency estimation)",
            "Driving time (in seconds)",
            "Number of curves in the route",
            "Power exherted (experimental, related to fuel efficiency estimation)",
            "Acceleration events (internal value)",
            "Braking events (internal value)",
            "Turning events (internal value)",
            "Longitudinal-distraction Global Score (internal value, combines mean[31] and std[32])",
            "Transversal-distraction Global Score (internal value, combines mean[33] and std[34])",
            "Mean Long.-dist. score (internal value)",
            "STD Long.-dist. score (internal value)",
            "Average Trans.-dist. score (internal value)",
            "STD Trans.-dist. score (internal value)",
            "Lacc (number of low accelerations)",
            "Macc (number of medium accelerations)",
            "Hacc (number of high accelerations)",
            "Lbra (number of low brakings)",
            "Mbra (number of medium brakings)",
            "Hbra (number of high brakings)",
            "Ltur (number of low turnings)",
            "Mtur (number of medium turnings)",
            "Htur (number of high turnings)",
            "Score total (base 100, direct mean of the other 7 scores [45-51])",
            "Score accelerations (base 100)",
            "Score brakings (base 100)",
            "Score turnings (base 100)",
            "Score lane-weaving (base 100)",
            "Score lane-drifting (base 100)",
            "Score overspeeding (base 100)",
            "Score car-following (base 100)",
            "Ratio normal (base 1)",
            "Ratio drowsy (base 1)",
            "Ratio aggressive (base 1)",
        ],
        "SEMANTIC_ONLINE.txt": [
            "TimeStamp since route start (seconds)",
            "GPS Latitude (degrees)",
            "GPS Longitude (degrees)",
            "Score total WINDOW (base 100, direct mean of the other 7 scores)",
            "Score accelerations WINDOW (base 100)",
            "Score brakings WINDOW (base 100)",
            "Score turnings WINDOW (base 100)",
            "Score weaving WINDOW (base 100)",
            "Score drifting WINDOW (base 100)",
            "Score overspeeding WINDOW (base 100)",
            "Score car-following WINDOW (base 100)",
            "Ratio normal WINDOW (base 1)",
            "Ratio drowsy WINDOW (base 1)",
            "Ratio aggressive WINDOW (base 1)",
            "Ratio distracted WINDOW (1=distraction detected in last 2 seconds, 0=otherwise)",
            "Score total (base 100, direct mean of the other 7 scores)",
            "Score accelerations (base 100)",
            "Score brakings (base 100)",
            "Score turnings (base 100)",
            "Score weaving (base 100)",
            "Score drifting (base 100)",
            "Score overspeeding (base 100)",
            "Score car-following (base 100)",
            "Ratio normal (base 1)",
            "Ratio drowsy (base 1)",
            "Ratio aggressive (base 1)",
            "Ratio distracted (1=distraction detected in last 2 seconds, 0=otherwise)",
        ],
    }

    def __init__(
        self,
        parent_path,
        driver_id,
        state_id,
        road_id,
        data_type_id,
        standard=True,
        verbose=0,
    ):
        """A constructor for the UahDatasetLoader class.

        Args:
        * parent_path (str): The path to the parent directory of the UahDataset.
        * driver_id (str or int): The number of the driver, can be an integer from `1` to `6` or a string that ends with integer in the same range such as `"driver1"` or `"D6"`.
        * state_id (str or int): The state of the driving session, can be an integer from `1` to `3` or a string such as `"normal"`,`"aggressive"` or `"drowsy"` not case sensitive.
        * road_id (str or int): The type of road in the driving session, can be an integer from `1` to `2` or a string such as `"motorway"` or `"secondary"` not case sensitive.
        * data_type_id (str or int): The type of data or the file of data chosen, can be an integer from 1 to 9 or a string such as `"gps"` or `"accelerometer"` not case sensitive.
        * standard (bool, optional): if `True` gives you the first session and if `False` gives the second session, of course for both cases it depends on the availability of the data. Defaults to `True`.
        * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1``. Defaults to ``0``.
        """
        super().__init__(
            parent_path,
            driver_id,
            state_id,
            road_id,
            data_type_id,
            standard,
            verbose=verbose,
        )
        if self.file == "SEMANTIC_FINAL.txt":
            delimiter = None
        else:
            delimiter = " "
        self.data = read_csv(self.file_path, delimiter=delimiter, header=None)
        if verbose == 1:
            print(f"\033[1m+++Data loaded successfully from {self.file} +++\033[0m\n")
        if self.file == self.SENSOR_FILES[0]:
            self.data = self.data.drop([9, 10, 11, 12], axis=1)
        elif self.file == self.SENSOR_FILES[1]:
            try:
                self.data = self.data.drop(11, axis=1)
            except Exception:
                self.data = self.data
        elif self.file == self.SENSOR_FILES[3]:
            self.data = self.data.drop(5, axis=1)
        elif self.file == self.SENSOR_FILES[4]:
            self.data = self.data.drop(10, axis=1)
        elif self.file == self.SENSOR_FILES[6]:
            self.data = self.data.drop(6, axis=1)
        elif self.file == self.SENSOR_FILES[7]:
            self.data = self.data.transpose()
        elif self.file == self.SENSOR_FILES[8]:
            self.data = self.data.drop(27, axis=1)
        self.data.columns = self.files_column_names[self.file]

    def __call__(self):
        """A method for the class instance call

        Returns:
            * pandas.DataFrame: The loaded data dataframe.
        """
        return self.data


class UAHDatasetBuilder:
    """A class to build a time series dataset from the UAHDataset using two files.includes a `data` attribute for the built UAHDataset, a `__call__ ` method for calling an instance of the class to return the `data` attribute.
    Args:
        * path (str): The path to the parent directory of the UahDataset.
        * datatype1 (str or int): The type of data or the file of data chosen for the first file, can be an integer from 1 to 9 or a string such as `"gps"` or `"accelerometer"` not case sensitive.
        * datatype2 (str or int): The type of data or the file of data chosen for the first file, can be an integer from 1 to 9 or a string such as `"gps"` or `"accelerometer"` not case sensitive.
        * window_size_dt1 (int, optional): The size of the first data window in the case of window stepping the data, if set to `0` will not perform the window stepping and if set to another value will perform window steping with mean transformation on the data. Defaults to `0`.
        * step_dt1 (int, optional): The length of the step for window stepping the first data, if smaller than `window_size_dt1` will result in overlapping windows, if equal to `window_size_dt1` performs standard window stepping, if bigger will skip some rows (not recommended). Defaults to `0`.
        * window_size_dt2 (int, optional): The size of the second data window in the case of window stepping the data, if set to `0` will not perform the window stepping and if set to another value will perform window steping with mean transformation on the data. Defaults to `0`.
        * step_dt2 (int, optional): The length of the step for window stepping the second data, if smaller than `window_size_dt2` will result in overlapping windows, if equal to `window_size_dt2` performs standard window stepping, if bigger will skip some rows (not recommended). Defaults to `0`.
        * save_to (str, optional): Can be `"csv"` or `"parquet"` or `None` if set to `"csv"` or `"parquet"` will save the dataset to the corresponding format in a newly created directory, if set to `None` will not save the dataset. Defaults to `None`.
        * name_dataset (str, optional): The name of the dataset in case of save_to is set to save the dataset. Defaults to "UAHDataset".
        * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1`` or ``2``or ``3``. Defaults to ``0``.
    """

    def __init__(
        self,
        path,
        datatype1,
        datatype2,
        window_size_dt1=0,
        step_dt1=0,
        window_size_dt2=0,
        step_dt2=0,
        save_to=None,
        name_dataset="UAHDataset",
        verbose=0,
    ):
        """A constructor for the UAHDatasetBuilder class.

        Args:
            * path (str): The path to the parent directory of the UahDataset.
            * datatype1 (str or int): The type of data or the file of data chosen for the first file, can be an integer from 1 to 9 or a string such as `"gps"` or `"accelerometer"` not case sensitive.
            * datatype2 (str or int): The type of data or the file of data chosen for the first file, can be an integer from 1 to 9 or a string such as `"gps"` or `"accelerometer"` not case sensitive.
            * window_size_dt1 (int, optional): The size of the first data window in the case of window stepping the data, if set to `0` will not perform the window stepping and if set to another value will perform window steping with mean transformation on the data. Defaults to `0`.
            * step_dt1 (int, optional): The length of the step for window stepping the first data, if smaller than `window_size_dt1` will result in overlapping windows, if equal to `window_size_dt1` performs standard window stepping, if bigger will skip some rows (not recommended). Defaults to `0`.
            * window_size_dt2 (int, optional): The size of the second data window in the case of window stepping the data, if set to `0` will not perform the window stepping and if set to another value will perform window steping with mean transformation on the data. Defaults to `0`.
            * step_dt2 (int, optional): The length of the step for window stepping the second data, if smaller than `window_size_dt2` will result in overlapping windows, if equal to `window_size_dt2` performs standard window stepping, if bigger will skip some rows (not recommended). Defaults to `0`.
            * save_to (str, optional): Can be `"csv"` or `"parquet"` or `None` if set to `"csv"` or `"parquet"` will save the dataset to the corresponding format in a newly created directory, if set to `None` will not save the dataset. Defaults to `None`.
            * name_dataset (str, optional): The name of the dataset in case of save_to is set to save the dataset. Defaults to "UAHDataset".
            * verbose (int, optional): An integer of the verbosity of the operation can be ``0`` or ``1`` or ``2``or ``3``. Defaults to ``0``.
        """
        self.data = DataFrame()
        count = 0
        for i in (1, 2, 3, 4, 5, 6):
            for j in (1, 2, 3):
                for k in (1, 2):
                    for standard in True, False:
                        try:
                            if verbose > 0:
                                print(
                                    f"\n\033[1m<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< CASE{count+1} STARTS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\033[0m\n"
                                )
                                print(
                                    "\n===========LOADING THE FIRST DATA FILE===========\n"
                                )
                            raw_data1 = UahDatasetReader(
                                path,
                                i,
                                j,
                                k,
                                datatype1,
                                standard=standard,
                                verbose=verbose,
                            )
                            if verbose > 0:
                                print(
                                    "\n===========CLEANING THE FIRST FILE DATA ===========\n"
                                )
                            data_chunk1 = DataCleaner(
                                raw_data1(),
                                window_size=window_size_dt1,
                                step=step_dt1,
                                window_transformation=True,
                                verbose=0,
                            ).dataset
                            if verbose > 0:
                                print(
                                    f"\033[1mFirst data shape is: {data_chunk1.shape}\033[0m"
                                )
                                print(
                                    "\n===========LOADING THE SECOND DATA FILE===========\n"
                                )
                            raw_data2 = UahDatasetReader(
                                path,
                                i,
                                j,
                                k,
                                datatype2,
                                standard=standard,
                                verbose=verbose,
                            )
                            if verbose > 0:
                                print(
                                    "\n===========CLEANING THE SECOND FILE DATA ===========\n"
                                )
                            data_chunk2 = DataCleaner(
                                raw_data2(),
                                window_size=window_size_dt2,
                                step=step_dt2,
                                window_transformation=True,
                                verbose=0,
                            ).dataset
                            if verbose > 0:
                                print(
                                    f"\033[1mSecond data shape is: {data_chunk2.shape}\033[0m"
                                )
                                print("\n===========MERGING DATA===========\n")
                            merge_verbose = 1 if verbose > 2 else 0
                            data_chunk_merged = DataCleaner(
                                data=data_chunk1,
                                merge_data=data_chunk2,
                                add_columns_dictionnary={
                                    "driver": raw_data1.driver,
                                    "road": raw_data1.road,
                                    "target": raw_data1.state,
                                },
                                verbose=merge_verbose,
                            ).dataset
                            if verbose > 0:
                                print(
                                    f"\033[1mMerged data shape is: {data_chunk_merged.shape}\033[0m"
                                )
                            self.data = self.data.append(data_chunk_merged)
                            self.data = self.data.reset_index()
                            self.data = self.data.drop("index", axis=1)
                            count += 1
                            if verbose > 0:
                                print(
                                    f"\n\033[1m<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< CASE{count} FINISHED >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\033[0m\n"
                                )
                        except ValueError:
                            if verbose > 0:
                                print(
                                    "\033[1mNO EXISTING FILE WITH THIS PATH...CONTINUE CASE WITH ANOTHER PATH\033[0m\n"
                                )
                                print(
                                    f"\n\033[1m<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< NEW CASE{count+1} ATTEMPT >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\033[0m\n"
                                )
        if verbose > 0:
            print(f"\n\033[1m...DATA BUILDING COMPLETE WITH {count} CASES\033[0m\n")
            print(f"\033[1mFINAL DATA SHAPE: {self.data.shape}\033[0m")
        PATH = "dataset"
        if save_to == "csv":
            save_csv(self.data, PATH, name_dataset, verbose=verbose)
        elif save_to == "parquet":
            save_parquet(self.data, PATH, name_dataset, verbose=verbose)

    def __call__(self):
        """A method for the class instance call

        Returns:
            * pandas.DataFrame: built dataset dataframe.
        """
        return self.data


class UAHDatasetLoader:
    def __init__(self, path=None, specific_section=None, read_from=None, verbose=0):
        """[summary]

        Args:
            * path (str, optional): The data file name in the working directory or the data file path with the file name used in case the dataset prarameter is not set. Defaults to `""`.
            * specific_section (str or int, optional): A parameter to define a specific grouping from the UAHdataset used in case the dataset prarameter is not set. Defaults to `None`.
            read_from ([type], optional): [description]. Defaults to None.
            verbose (int, optional): [description]. Defaults to 0.

        Raises:
            ValueError: [description]
            ValueError: [description]
            ValueError: [description]
        """
        if read_from is None:
            read_from = "csv"
        elif read_from != "csv" and read_from != "parquet":
            raise ValueError("read_from parameter is unavailable or an Unkown format.")
        if path is None:
            path = pkg_resources.resource_filename(
                __name__, f"dataset/UAHDataset.{read_from}"
            )
            print(f"\nLoading the internal \033[1mUAHDataset\033[0m from maaml\n")
        if read_from == "csv":
            try:
                self.data = read_csv(path, delimiter=",", header=0, verbose=verbose)
            except Exception:
                raise ValueError("Verify the provided path.")
        elif read_from == "parquet":
            try:
                self.data = read_parquet(path, verbose=verbose)
            except Exception:
                raise ValueError("Verify the provided path for the parquet file.")
        if specific_section is None:
            data_info = "full data loaded successfully\n"
        elif str(specific_section) == "secondary road" or str(specific_section) == "":
            self.data = self.data.loc[self.data["road"] == "secondary"]
            self.data = self.data.drop("road", axis=1)
            data_info = "data of secondary road loaded successfully"
        elif str(specific_section) == "motorway road" or str(specific_section) == "0":
            self.data = self.data.loc[self.data["road"] == "motorway"]
            self.data = self.data.drop("road", axis=1)
            data_info = "data of motorway road loaded successfully"
        elif int(specific_section) < 7:
            self.data = self.data.loc[self.data["driver"] == int(specific_section)]
            self.data = self.data.drop("driver", axis=1)
            data_info = (
                f"data of driver number {int(specific_section)} loaded successfully \n"
            )
        else:
            raise ValueError("Wrong specific_section entry.")
        if verbose == 1:
            print(data_info)

    def __call__(self):
        """A method for the class instance call

        Returns:
            * pandas.DataFrame: built dataset dataframe.
        """
        return self.data


if __name__ == "__main__":
    DATA_DIR_PATH = "/run/media/najem/34b207a8-0f0c-4398-bba2-f31339727706/home/stock/The_stock/dev & datasets/PhD/datasets/UAH-DRIVESET-v1/"
    dataset = UAHDatasetBuilder(
        DATA_DIR_PATH,
        "gps",
        "acc",
        window_size_dt2=10,
        step_dt2=10,
        verbose=2,
    )
