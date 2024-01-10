import sys, os, csv, xml.etree.cElementTree as ET, re, json, datetime


def regex_replace(company, input, delimiter):
    with open(input, newline="", encoding="utf-8") as list:
        file = csv.reader(list, delimiter=delimiter)
        for row in file:
            mode = row[2].strip()
            file_value = row[0].strip().lower()
            if (
                mode == "regex"
                and file_value.find("*") == 0
                and file_value.rfind("*") == (len(file_value) - 1)
            ):
                if re.search(
                    r"\b(" + file_value.rstrip("*").lstrip("*") + r")\b",
                    company.lower(),
                ):
                    return row[1].strip()
            elif mode == "regex" and file_value.find("*") == (len(file_value) - 1):
                if re.match(r"^\b(" + file_value.rstrip("*") + r")\b", company.lower()):
                    return row[1].strip()
            elif file_value == company.lower():
                return row[1].strip()
        return False


def comparison(input, id, tickettype, delimiter):
    if type(input) is list:
        value_based_comparison(el, id, tickettype)

    elif os.path.exists(input) and os.path.isfile(input):
        if file_based_comparison(input, id, tickettype, delimiter):
            return True
        return False

    elif type(input) is str or type(input) is int:
        el = input.split(delimiter)
        if value_based_comparison(el, id, tickettype):
            return True
        return False

    else:
        print("Type of '" + input + "' cannot be processed.")
        sys.exit(1)


def compare_values(e, id, tickettype):
    # if type(e) is int:
    #     print("now here")
    #     for e in input:
    #         if str(e.strip()) == str(id.strip()):
    #             return True
    #     return False
    if e.isnumeric():
        if str(e.strip()) == str(id.strip()):
            return True

    elif type(e) is str:
        if e.strip() == tickettype.strip():
            print(id)
            return True
        # for e in input:
        #     if e.strip() == tickettype.strip():
        #         return True
        #     return False


def value_based_comparison(input, id, tickettype):
    for e in input:
        if compare_values(e, id, tickettype):
            return True


def file_based_comparison(input, id, tickettype, delimiter):
    with open(input, newline="", encoding="utf-8") as list:
        file = csv.reader(list, delimiter=delimiter)
        for row in file:
            if compare_values(row[0], id, tickettype):
                return True


def create_xml(
    input,
    delimiter,
    output,
    name,
    no_qrcode,
    speaker,
    vc,
    vip,
    press,
    tickettype_input,
    company_input,
    eventdiff,
    event,
    no_meta,
):
    timestamp_create = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    parent = ET.Element("event")
    if name:
        ET.SubElement(parent, "title").text = name

    ET.SubElement(parent, "checkin").text = "true" if no_qrcode == False else "false"
    attendees = ET.SubElement(parent, "attendees")

    with open(input, newline="", encoding="utf-8") as csvfile:
        attendee_list = csv.reader(csvfile, delimiter=delimiter)
        columns = len(next(attendee_list))
        if columns < 3:
            print(
                "You need to specify at least 'id', 'firstname' and 'lastname' in your input file. Please go back to the scratchboard :P."
            )
            sys.exit(0)
        for row in attendee_list:
            # set csv output values to variables
            id = row[0]
            lastname = row[1]
            firstname = row[2]
            company = row[3] if columns >= 4 else ""
            tickettype = row[4] if columns >= 5 else ""
            barcode = row[5] if columns >= 6 else ""
            eventid = row[6] if columns >= 7 else ""
            eventno = row[7] if columns >= 8 else ""

            display_company = (
                regex_replace(company, company_input, delimiter)
                if company_input
                else False
            )
            display_tickettype = (
                regex_replace(tickettype, tickettype_input, delimiter)
                if tickettype_input
                else False
            )

            event_identifier = (
                eventdiff.split(",")[int(eventno) - 1]
                if eventdiff and len(eventdiff.split(",")) >= len(event.split(","))
                else eventno
                if eventdiff
                else ""
            )

            # display tickettype in case it did not match with one of the file-entries
            # that way user can make sure to add the company to the file if necessary
            if display_tickettype is False:
                print('WARNING: "' + row[4] + '" has not been set as a tickettype')

            attendee = ET.SubElement(attendees, "attendee")

            ET.SubElement(attendee, "id").text = id.strip() if no_meta == False else ""
            ET.SubElement(attendee, "timestamp").text = (
                timestamp_create if no_meta == False else ""
            )
            ET.SubElement(attendee, "name").text = firstname + " " + lastname
            ET.SubElement(attendee, "company").text = (
                display_company if display_company else company if company else "–"
            )

            if barcode:
                ET.SubElement(attendee, "entrancecode").text = barcode

            ET.SubElement(attendee, "tickettype").text = (
                display_tickettype
                if display_tickettype
                else tickettype
                if tickettype
                else "-"
            )

            ET.SubElement(attendee, "eventid").text = (
                eventid.strip() if no_meta == False else ""
            )
            ET.SubElement(attendee, "eventtitle").text = (
                event_identifier
                if len(event_identifier) <= 8
                else event_identifier[:6] + "…"
            )

            ET.SubElement(attendee, "speaker").text = (
                "true"
                if speaker and comparison(speaker, id, tickettype, delimiter)
                else "false"
            )
            ET.SubElement(attendee, "vip").text = (
                "true"
                if vip and comparison(vip, id, tickettype, delimiter)
                else "false"
            )
            ET.SubElement(attendee, "vc").text = (
                "true" if vc and comparison(vc, id, tickettype, delimiter) else "false"
            )
            ET.SubElement(attendee, "press").text = (
                "true"
                if press and comparison(press, id, tickettype, delimiter)
                else "false"
            )

        tree = ET.ElementTree(parent)
        tree.write(output + ".xml", encoding="UTF-8", xml_declaration=True)

        return_value = {"output": output + ".xml", "output_name": output}
        return json.dumps(return_value)
