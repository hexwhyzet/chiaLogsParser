import datetime
import glob
import os
import re
from dataclasses import dataclass
from typing import List

from config import Config

config = Config()


def cut(paths):
    """
    >>> cut(["user1/dir1/logs.log", "user1/dir2/logs.log", "user2/dir1/logs.log", "user1/dir1/logs2.log"])
    ['user1/dir1/logs.log', 'dir2/logs.log', 'user2/dir1/logs.log', 'logs2.log']

    The function maximally shortens paths leaving them unique.
    """
    cut_paths = []

    for path in paths:
        split_path = path.split("/")
        max_end_similarity = 0
        for second_path in paths:
            if path != second_path:
                split_second_path = second_path.split("/")
                last_similar_name = 0
                while last_similar_name < len(split_path) \
                        and last_similar_name < len(split_second_path) \
                        and split_path[-last_similar_name - 1] == split_second_path[-last_similar_name - 1]:
                    last_similar_name += 1
                max_end_similarity = max(max_end_similarity, last_similar_name)
        cut_paths += ["/".join(split_path[-max_end_similarity - 1:])]

    return cut_paths


def get_logs_paths():
    """
    Looks for .log files in directories said in config.json
    """
    paths = []

    for logs_dir in config["logs_directories"]:
        paths += glob.glob(os.path.join(os.path.abspath(logs_dir), "*.log"))

    # Windows backslashes to forward slashes
    paths = list(map(lambda x: x.replace("\\", "/"), paths))

    return list(zip(cut(paths), paths))


def does_this_log_filepath_exists(path):
    return path in list(map(lambda x: x[1], get_logs_paths()))


def split_without_deleting_delimiter(delimiter, text):
    return [e + delimiter for e in text.split(delimiter) if e]


def td_to_str(timedelta: datetime.timedelta):
    """
    Converts timedelta to short string for telegram
    """
    seconds = int(timedelta.total_seconds())
    days = seconds // (60 * 60 * 24)
    hours = seconds % (60 * 60 * 24) // (60 * 60)
    minutes = seconds % (60 * 60) // 60
    seconds = seconds % 60
    if days > 0:
        return f"{days}d{hours if hours else ''}"
    if hours > 0:
        return f"{hours}h{minutes if minutes else ''}"
    if minutes > 0:
        return f"{minutes}m{seconds if seconds else ''}"
    else:
        return f"{seconds}s"


@dataclass
class PhaseData:
    time: datetime.timedelta


class PlotData:
    """
    Information about creation of single plot
    """
    phases: List[PhaseData]
    total_time: datetime.timedelta

    @staticmethod
    def phase_line(text, phase_num):
        results = re.findall(fr"Time for phase {phase_num}.*\n", text)
        return results[0]

    @staticmethod
    def time_for_phase(text, phase_num):
        line = PlotData.phase_line(text, phase_num)
        time = datetime.timedelta(seconds=int(float(re.findall(r"\d+\.\d+", line)[0])))
        return time

    @staticmethod
    def total_time(text):
        line = re.findall(fr"Total time.*\n", text)[0]
        time = datetime.timedelta(seconds=int(float(re.findall(r"\d+\.\d+", line)[0])))
        return time

    def __init__(self, text):
        self.phases = [
            PhaseData(PlotData.time_for_phase(text, 1)),
            PhaseData(PlotData.time_for_phase(text, 2)),
            PhaseData(PlotData.time_for_phase(text, 3)),
            PhaseData(PlotData.time_for_phase(text, 4)),
        ]
        self.total_time = PlotData.total_time(text)


class LogsData:
    """
    Information about creation of plots in whole .log file
    """
    plots: List[PlotData]

    def __init__(self, filepath):
        self.plots = []
        with open(filepath, "r", encoding="utf-8") as file:
            first_plot = True
            plot_text = ""
            new_line = file.readline()
            while new_line:
                if new_line.startswith("Starting plotting progress"):
                    if not first_plot:
                        self.plots += [PlotData(plot_text)]
                    first_plot = False
                    plot_text = new_line
                else:
                    plot_text += new_line
                new_line = file.readline()

    def telegram_format(self):
        table = [("n", "P1", "P2", "P3", "P4", "T")]
        for i in range(len(self.plots)):
            line = [str(i + 1)]
            plot = self.plots[i]
            for j in range(4):
                if j < len(plot.phases):
                    line += [td_to_str(plot.phases[j].time)]
                else:
                    line += ["-"]
            line += [td_to_str(plot.total_time)]
            table += [line]

        new_table = ""
        column_widths = [len(max(table, key=lambda x: len(str(x[i])))[i]) + 1 for i in range(len(table[0]))]
        for line in table:
            new_table += "".join(line[i].ljust(column_widths[i]) for i in range(len(table[0]))) + "\n"
        return new_table
