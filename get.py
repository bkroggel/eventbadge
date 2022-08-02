from ast import AsyncFunctionDef
import requests, sys, getopt, csv, shutil, json
from tempfile import NamedTemporaryFile


def get_eventbrite(api_token, eventid):
    requestheaders = {"Authorization": "Bearer " + api_token}

    attendees = []
    continuation_token = ""
    current_page = 0
    last_page = 1

    while current_page < last_page:
        print("Current Page: " + str(current_page) + " | Last Page: " + str(last_page))
        r = requests.get(
            "https://www.eventbriteapi.com/v3/events/"
            + eventid
            + "/attendees/"
            + ("?continuation=" + continuation_token if continuation_token else ""),
            headers=requestheaders,
        )
        attendees += r.json()["attendees"]
        print(len(attendees))
        current_page = r.json()["pagination"]["page_number"]
        last_page = r.json()["pagination"]["page_count"]
        if current_page != last_page:
            continuation_token = r.json()["pagination"]["continuation"]

    return attendees


def create_csv(attendees, output, delimiter):
    tempfile = NamedTemporaryFile(mode="w", delete=False)
    with open(tempfile.name, "w", newline="", encoding="utf-8") as tempfile:
        writer = csv.writer(tempfile, delimiter=delimiter)
        writer.writerow(
            [
                "userid",
                "lastname",
                "firstname",
                "company",
                "tickettype",
                "barcode",
                "order no.",
            ]
        )
        for attendee in attendees:
            row = ["", "", "", "", "", "", ""]
            row[0] = attendee["id"]
            row[1] = attendee["profile"]["last_name"]
            row[2] = attendee["profile"]["first_name"]
            row[3] = attendee["profile"]["company"]
            row[4] = attendee["ticket_class_name"]
            row[5] = attendee["barcodes"][0]["barcode"]
            row[6] = attendee["order_id"]

            writer.writerow(row)

    shutil.move(tempfile.name, output + ".csv")


def get_attendees(api_token, eventid, output, delimiter):
    attendees = get_eventbrite(api_token, eventid)
    create_csv(attendees, output, delimiter)

    return_values = {"output": output + ".csv"}
    return json.dumps(return_values)
