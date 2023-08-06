"""
Convert YAML front matter to CSV
"""

from queue import Empty
from typing import Dict
from durations import Duration
import os
import frontmatter
import csv

filtered = dict()
fields = {
    "name": "Name",
    "playtime": "Playtime",
    "platform": "Platform",
    "infinite": "Infinite",
    "finished": "Finished",
    "refunded": "Refunded",
    "dropped": "Dropped",
    "date-released": "DateReleased",
    "date-purchased": "DatePurchased",
    "date-started": "DateStarted",
    "date-finished": "DateFinished",
}


def convert(directory="f", outputfile="test.csv"):
    if not os.path.isdir(directory):
        exit(f"The directory {directory} does not exist!")
    with open(outputfile, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields.values())
        writer.writeheader()
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)

            if os.path.isfile(f):
                article = frontmatter.load(f)
                for field in fields:
                    if field not in article.metadata.keys():
                        newvalue = ""
                    else:
                        newvalue = article.metadata[field]
                    if field == "playtime" and newvalue != 0 and newvalue is not None:
                        if type(newvalue) is dict:
                            totalvalue = 0
                            for key in newvalue:
                                timevalue = Duration(newvalue[key]).to_hours()
                                totalvalue += timevalue
                            newvalue = totalvalue
                        else:
                            timevalue = Duration(newvalue)
                            newvalue = timevalue.to_hours()
                    if type(newvalue) is list:
                        print(
                            f"Field '{field}' for file '{filename}' is a list, joining with commas."
                        )
                        newvalue = ",".join(newvalue)
                    filtered[fields[field]] = newvalue

                writer.writerow(filtered)


if __name__ == "__main__":
    convert()
