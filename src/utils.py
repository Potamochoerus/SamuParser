import requests
import pandas as pd
import json
import pickle
from dotenv import load_dotenv
from os import getenv
from pathlib import Path
import shutil
import time

## Load .env variables
load_dotenv()
API_KEY = getenv("BALLCHASING_API_KEY")
HEADERS = {"Authorization": API_KEY}


def upload_replay(filepath):
    """
    Upload replay to ballchasing API

    :param filepath: .replay file from rocket league
    """

    with open(filepath, "rb") as f:
        r = requests.post(
            "https://ballchasing.com/api/v2/upload", headers=HEADERS, files={"file": f}
        )
    time.sleep(2)
    return r.json()["id"]


def upload_replay_folder(folderpath, outpath, logfile):
    """
    Upload a folder of replays

    :param folderpath: Folder containing the .replay files
    :param outpath: Folder to move the processed files
    """
    assert folderpath.is_dir(), "folderpath is not a folder"
    assert outpath.is_dir(), "outpath is not a folder"
    assert logfile.is_file(), "logfile is not a file"

    replay_files = list(Path(folderpath).glob("*.replay"))
    assert len(replay_files) > 0, "No .replay files to process"

    print(f"About to upload {len(replay_files)} to Ballchasing.com")
    uploaded_files = [upload_replay(file) for file in replay_files]
    assert len(replay_files) == len(
        uploaded_files
    ), "Problem occured during file uploading."
    print(f"Upload complete.")

    [shutil.move(str(f), outpath / f.name) for f in replay_files]
    with open(logfile, "a") as f:
        f.write("\n".join(uploaded_files) + "\n")
    return uploaded_files

# Get stats
def get_replay_stats(replay_id):
    r = requests.get(
        f"https://ballchasing.com/api/replays/{replay_id}", headers=HEADERS
    )
    time.sleep(1)
    return r.json()


# Flatten to pandas
def to_pandas(stats):
    rows = []
    for team in ["blue", "orange"]:
        for player in stats[team]["players"]:
            row = {
                "team": team,
                "player": player["name"],
                "id": player["id"]["id"],
                "timestamp": stats["date"],
                "gamelength": player["end_time"]
            }
            # flatten all stat categories
            for category, values in player["stats"].items():
                for k, v in values.items():
                    row[f"{category}_{k}"] = v
            rows.append(row)
    df = pd.DataFrame(rows)
    return df


def process_batch_replay_stats(replay_list, parsed_folder):
    """
    Process a batch of replay stats

    :param replay_list: A list of replay IDs
    """
    assert len(replay_list) > 0, "No replay to process"
    for replay_id in replay_list:
        outfile = Path(parsed_folder / f"{replay_id}.pkl")
        stats = get_replay_stats(replay_id)
        df = to_pandas(stats)
        df.to_pickle(outfile)


def merge_processed_replays(parsed_folder, outfile):
    """
    Merge all processed replays into one pkl file

    :param parsed_folder: Folder where the .pkl files are located
    :param outfile: Output .pkl merged file
    """
    assert parsed_folder.is_dir(), "parsed_folder is not a folder"
    assert outfile.is_file(), "outfile is not a file"

    replay_files = list(Path(parsed_folder).glob("*.pkl"))
    replay_list = [pd.read_pickle(f) for f in replay_files]
    assert len(replay_list) > 0, "No parsed replays detected"
    assert all(
        isinstance(df, pd.DataFrame) for df in replay_list
    ), "Not all loaded replays are parsed pandas dataframes"
    replay_db = pd.concat(replay_list, ignore_index=True)
    replay_db.to_pickle(outfile)
    return
