#!/usr/bin/python
import sys, argparse
from parse import create_xml
from create import create_tag
from get import get_attendees
import datetime
import json
import os


def create(args):
    print("Going to create something…")
    print("Stay tuned!")
    print("▼ ---")
    # print(args)

    if not args.output:
        args.output = datetime.datetime.now().strftime("%Y%m%d") + "-nametags"

    if args.input and args.delimiter:
        c = create_xml(
            args.input,
            args.delimiter,
            args.output,
            args.name,
            args.qrcode,
            args.speaker,
            args.vc,
            args.vip,
            args.press,
            args.types,
            args.company,
        )
        output_name = json.loads(c)["output_name"]
        create_tag(output_name)
    elif args.token and args.event:
        g = get_attendees(args.token, args.event, args.output, args.delimiter)
        csv_output = json.loads(g)["output"]
        c = create_xml(
            csv_output,
            ",",
            args.output,
            args.name,
            args.qrcode,
            args.speaker,
            args.vc,
            args.vip,
            args.press,
            args.types,
            args.company,
        )
        xml_output = json.loads(c)["output"]

        create_tag(xml_output, args.output)

        if os.path.isfile(csv_output):
            os.remove(csv_output)

        if os.path.isfile(xml_output):
            os.remove(xml_output)
    elif args.input and args.delimiter is None:
        print(
            "CSV-File is present but no delimiter is specified. Please add -d to your command."
        )
        sys.exit(1)
    elif args.token and args.event is None:
        print(
            "API token is specified but no event has been selected. Please add the event_id via -e to your command."
        )
        sys.exit(1)
    elif args.input is None and args.token is None:
        print(
            "It seems like you have not specified a csv or api token input. Please do so by using the -i or -t flag or make use of the --help command for further information."
        )
        sys.exit(1)


def get(args):
    print(args)


def main(argv):

    parser = argparse.ArgumentParser(
        prog="PROG",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Just some description",
    )
    subparsers = parser.add_subparsers(
        help="sub-command help"
    )  # default parser for subcommands
    input_parser = argparse.ArgumentParser(
        add_help=False
    )  # subcommand parent for utilizing the input flags

    csv = input_parser.add_argument_group("CSV Input")
    csv.add_argument(
        "-i",
        "--input",
        help="csv file containing a list of attendees (id, lastname, firstname, company, tickettype, barcode|registrationcode, orderid)",
    )
    csv.add_argument(
        "-d",
        "--delimiter",
        choices=[",", ";"],
        default=",",
        help="delimiter of input and output file – defaults to ','",
    )

    api = input_parser.add_argument_group("API Input")
    api.add_argument(
        "-t",
        "--token",
        help="string. eventbrite api token — can be accessed here: https://www.eventbrite.com/platform/api-keys",
    )
    api.add_argument(
        "-e",
        "--event",
        help="string eventbrite key to respective happening. Can be accessed from URL of event.",
    )
    input_parser.add_argument(
        "-o",
        "--output",
        help="specifiy the name of the output file. Defaults to 'YYYY-MM-DD-eventname'",
    )
    parser_create = subparsers.add_parser(
        "create", parents=[input_parser], help="command to actually create namebadges"
    )
    parser_create.set_defaults(func=create)

    parser_get = subparsers.add_parser(
        "get", parents=[input_parser], help="command to actually create namebadges"
    )
    parser_get.set_defaults(func=get)

    attendee_groups = parser_create.add_argument_group(
        "Attendee Groups",
        "allows to display the access groups of the attendees directly on the namebadges",
    )
    attendee_groups.add_argument("--vip")
    attendee_groups.add_argument("--speaker")
    attendee_groups.add_argument("--vc")
    attendee_groups.add_argument("--press")
    parser_create.add_argument(
        "-n",
        "--name",
        help="string. name which will be placed on top of the nametag. If property is set but no input provided the eventbrite name of the event will be used.",
    )
    parser_create.add_argument(
        "--qrcode",
        action="store_true",
        default=True,
        help="flag which controls the visibility of a barcode that allows to checkin attendees. Defaults to true but will omitted if no barcode values are present in csv-input. Eventbrite pulls will include the information in any case.",
    )

    parser_create.add_argument("--types", nargs="?", const=True)
    parser_create.add_argument("--company", nargs="?", const=True)

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])