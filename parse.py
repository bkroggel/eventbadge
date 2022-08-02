import sys, os, csv, xml.etree.cElementTree as ET, re, json


def regex_replace(input, company):
    with open(input, newline="", encoding="utf-8") as list:
        file = csv.reader(list, delimiter=";")
        for row in file:
            mode = row[2].strip()
            file_value = row[0].strip()
            if (
                mode == "regex"
                and file_value.find("*") == 0
                and file_value.rfind("*") == (len(file_value) - 1)
            ):
                if re.search(
                    r"\b(" + file_value.rstrip("*").lstrip("*") + r")\b", company
                ):
                    return row[1].strip()
            elif mode == "regex" and file_value.find("*") == (len(file_value) - 1):
                if re.match(r"^\b(" + file_value.rstrip("*") + r")\b", company):
                    return row[1].strip()
            elif file_value == company:
                return row[1].strip()
        return False


def comparison(input, id, tickettype, delimiter):
    if type(input) is list:
        value_based_comparison(el, id, tickettype)

    elif os.path.exists(input) and os.path.isfile(input):
        file_based_comparison(input, id, tickettype, delimiter)

    elif type(input) is str or type(input) is int:
        el = input.split(delimiter)
        value_based_comparison(el, id, tickettype)

    else:
        print("Type of '" + input + "' cannot be processed.")
        sys.exit(1)


def compare_values(e, int, str):
    if type(e) is int:
        for e in input:
            if str(e.strip()) == str(int.strip()):
                return True
        return False

    elif type(e) is str:
        for e in input:
            if e.strip() == str.strip():
                return True
            return False


def value_based_comparison(input, id, tickettype):
    for e in input:
        compare_values(e, id, tickettype)


def file_based_comparison(input, id, tickettype, delimiter):
    with open(input, newline="", encoding="utf-8") as list:
        file = csv.reader(list, delimiter=delimiter)
        for row in file:
            compare_values(row[0], id, tickettype)


def create_xml(
    input,
    delimiter,
    output,
    name,
    qrcode,
    speaker,
    vc,
    vip,
    press,
    tickettype_input,
    company_input,
):
    parent = ET.Element("event")
    ET.SubElement(parent, "title").text = name
    ET.SubElement(parent, "checkin").text = "true" if qrcode == True else "false"
    attendees = ET.SubElement(parent, "attendees")

    with open(input, newline="", encoding="utf-8") as csvfile:
        attendee_list = csv.reader(csvfile, delimiter=delimiter)
        columns = len(next(attendee_list))
        print(columns)
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
            company = row[3] if columns >= 3 else ""
            tickettype = row[4] if columns >= 4 else ""
            barcode = row[5] if columns >= 5 else ""

            display_company = (
                regex_replace(company, company_input) if company_input else False
            )
            display_tickettype = (
                regex_replace(tickettype, tickettype_input)
                if tickettype_input
                else False
            )

            # display tickettype in case it did not match with one of the file-entries
            # that way user can make sure to add the company to the file if necessary
            if display_tickettype is False:
                print('WARNING: "' + row[3] + '" has not been set as a tickettype')

            attendee = ET.SubElement(attendees, "attendee")

            ET.SubElement(attendee, "name").text = firstname + " " + lastname
            ET.SubElement(attendee, "company").text = (
                display_company if display_company else company
            )
            ET.SubElement(attendee, "entrancecode").text = barcode
            ET.SubElement(attendee, "tickettype").text = (
                tickettype if tickettype else "-"
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
