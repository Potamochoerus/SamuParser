from src.utils import (
    process_batch_replay_stats,
    upload_replay_folder,
    merge_processed_replays,
)
from src.shared import RAW, PROCESSED, PARSED, MERGED, LOGFILE
import argparse


def main(args):
    assert args.convert or args.merge, "Please select convert or merge"
    if args.convert:
        uploaded_ids = upload_replay_folder(RAW, PROCESSED, LOGFILE)
        process_batch_replay_stats(uploaded_ids, PARSED)
        print(f"All submitted replays are converted.")

    if args.merge:
        merge_processed_replays(PARSED, MERGED)
        print(f"All parsed replays are merged.")

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SamuParse - Parse replay files from Rocket League using Ballchasing.com API."
    )

    parser.add_argument("--convert", action="store_true", help="Convert replays")
    parser.add_argument(
        "--merge", action="store_true", help="Merge converted replays for SamuTracker"
    )

    args = parser.parse_args()
    main(args)
