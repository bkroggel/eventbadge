import requests, csv, shutil, json
from tempfile import NamedTemporaryFile


def get_eventbrite(api_token, eventid):
    requestheaders = {"Authorization": "Bearer " + api_token}

    attendees = []
    events = eventid.split(",")

    for event in events:
        continuation_token = ""
        current_page = 1
        last_page = 1
        print(
            "Running Event No. "
            + str(events.index(event) + 1)
            + " of "
            + str(len(events))
        )

        while current_page <= last_page:
            updated_attendees = []
            print(
                "Current Page: " + str(current_page) + " | Last Page: " + str(last_page)
            )
            r = requests.get(
                "https://www.eventbriteapi.com/v3/events/"
                + event
                + "/attendees/"
                + ("?continuation=" + continuation_token if continuation_token else ""),
                headers=requestheaders,
            )
            for attendee in r.json()["attendees"]:
                attendee.update({"event_no": str(events.index(event) + 1)})
                updated_attendees.append(attendee)

            attendees += filter(
                lambda x: x["status"] == "Attending" or "Checked In",
                updated_attendees,
            )

            # attendees += filter(
            #     lambda x: x["status"] == "Attending" or "Checked In",
            #     r.json()["attendees"],
            # )
            print("No. of Attendees: " + str(len(attendees)))
            last_page = r.json()["pagination"]["page_count"]
            # last_page = 1
            if current_page != last_page:
                continuation_token = r.json()["pagination"]["continuation"]
            current_page += 1

    print("Overall No. of Attendees: " + str(len(attendees)))
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
                "event id",
                "event no.",
            ]
        )
        for attendee in attendees:
            row = ["", "", "", "", "", "", "", "", ""]
            row[0] = attendee["id"].strip()
            row[1] = attendee["profile"]["last_name"].strip()
            row[2] = attendee["profile"]["first_name"].strip()
            row[3] = (
                attendee["profile"]["company"].strip()
                if "company" in attendee["profile"]
                else attendee["profile"]["email"].split("@")[1]
                if "email" in attendee["profile"]
                else ""
            )
            row[4] = attendee["ticket_class_name"].strip()
            row[5] = attendee["barcodes"][0]["barcode"].strip()
            row[6] = attendee["event_id"].strip()
            row[7] = attendee["event_no"].strip()

            writer.writerow(row)

    shutil.move(tempfile.name, output + ".csv")


def get_attendees(api_token, eventid, output, delimiter):
    attendees = get_eventbrite(api_token, eventid)
    create_csv(attendees, output, delimiter)

    return_values = {"output": output + ".csv"}
    return json.dumps(return_values)


def read_csv_as_json(input, delimiter):
    with open(input, newline="", encoding="utf-8") as csvfile:
        attendees = []
        list = csv.reader(csvfile, delimiter=delimiter)
        next(list)
        for item in list:
            attendee = {}
            attendee["id"] = item[0]
            attendee["profile"] = {}
            attendee["profile"]["last_name"] = item[1]
            attendee["profile"]["first_name"] = item[2]
            attendee["profile"]["company"] = item[3]
            attendee["ticket_class_name"] = item[4]
            attendee["barcodes"] = [{"barcode": item[5]}]
            attendees.append(attendee)
    return json.dumps(attendees)


def build_company_list(attendees, delimiter):
    attendees.sort(
        key=lambda x: (x["profile"]["company"].lower().strip())
        if "company" in x["profile"]
        else x["profile"]["email"].split("@")[1]
        if "email" in x["profile"]
        else ""
    )
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
            company = (
                attendee["profile"]["company"]
                if "company" in attendee["profile"]
                else attendee["profile"]["email"].split("@")[1]
                if "email" in attendee["profile"]
                else ""
            )
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
