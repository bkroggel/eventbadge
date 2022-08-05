import requests, csv, shutil, json
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
        # last_page = r.json()["pagination"]["page_count"]
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
            row[0] = attendee["id"].strip()
            row[1] = attendee["profile"]["last_name"].strip()
            row[2] = attendee["profile"]["first_name"].strip()
            row[3] = attendee["profile"]["company"].strip()
            row[4] = attendee["ticket_class_name"].strip()
            row[5] = attendee["barcodes"][0]["barcode"].strip()
            row[6] = attendee["order_id"].strip()

            writer.writerow(row)

    shutil.move(tempfile.name, output + ".csv")


def get_attendees(api_token, eventid, output, delimiter):
    attendees = get_eventbrite(api_token, eventid)
    create_csv(attendees, output, delimiter)

    return_values = {"output": output + ".csv"}
    return json.dumps(return_values)


def build_company_list(attendees, delimiter):
    attendees.sort(key=lambda x: x["profile"]["company"].lower().strip())
    companies = []

    tempfile = NamedTemporaryFile(mode="w", delete=False)
    with open(tempfile.name, "w", newline="", encoding="utf-8") as tempfile:
        writer = csv.writer(tempfile, delimiter=delimiter)
        writer.writerow(
            [
                "rule",
                "definition",
                "type",
            ]
        )
        for attendee in attendees:
            company = attendee["profile"]["company"]
            if company not in companies:
                companies.append(company)
                row = ["", "", ""]
                row[0] = company.strip()
                row[2] = "string"

                writer.writerow(row)

    shutil.move(tempfile.name, "companies.csv")


def build_tickettype_list(attendees, delimiter):
    attendees.sort(
        key=lambda x: x["ticket_class_name"].lower().strip()
        if x["ticket_class_name"]
        else ""
    )
    tickettypes = []

    tempfile = NamedTemporaryFile(mode="w", delete=False)
    with open(tempfile.name, "w", newline="", encoding="utf-8") as tempfile:
        writer = csv.writer(tempfile, delimiter=delimiter)
        writer.writerow(
            [
                "rule",
                "colorcode",
                "type",
            ]
        )
        for attendee in attendees:
            tickettype = attendee["ticket_class_name"]
            if tickettype and tickettype.strip() and tickettype not in tickettypes:
                tickettypes.append(tickettype)
                row = ["", "", ""]
                row[0] = tickettype.strip()
                row[2] = "string"

                writer.writerow(row)

    shutil.move(tempfile.name, "tickettypes.csv")
