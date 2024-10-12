import datetime
import uuid

def parse_event_line(line):
    """
    Parses a single line of the input file and extracts the start datetime, end datetime, and description.

    Parameters:
        line (str): A line from the input file.

    Returns:
        tuple: (start_datetime, end_datetime, description) if parsing is successful.
        None: If parsing fails.
    """
    try:
        # Split the line into datetime part and description
        datetime_part, description = line.split(': ', 1)
        start_str, end_str = datetime_part.split(' - ')

        # Define the expected datetime format
        datetime_format = '%Y-%m-%d %H:%M:%S'

        # Parse the start and end datetime strings into datetime objects
        start_dt = datetime.datetime.strptime(start_str.strip(), datetime_format)
        end_dt = datetime.datetime.strptime(end_str.strip(), datetime_format)

        return start_dt, end_dt, description.strip()
    except Exception as e:
        print(f"Error parsing line: {line}\n{e}")
        return None

def escape_ics_text(text):
    """
    Escapes characters in text according to iCalendar (ICS) specifications.

    Parameters:
        text (str): The text to escape.

    Returns:
        str: Escaped text.
    """
    return text.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')

def create_ics(events, filename='output.ics'):
    """
    Creates an ICS file from a list of events.

    Parameters:
        events (list): List of tuples containing (start_datetime, end_datetime, description).
        filename (str): Name of the output ICS file.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        # Write the calendar header
        f.write("BEGIN:VCALENDAR\n")
        f.write("VERSION:2.0\n")
        f.write("PRODID:-//Your Organization//Your Product//EN\n")

        for event in events:
            start_dt, end_dt, description = event
            uid = str(uuid.uuid4()) + "@yourdomain.com"  # Ensure uniqueness
            dtstamp = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
            dtstart = start_dt.strftime('%Y%m%dT%H%M%S')
            dtend = end_dt.strftime('%Y%m%dT%H%M%S')

            # Escape special characters in description
            escaped_description = escape_ics_text(description)

            # Write the event details
            f.write("BEGIN:VEVENT\n")
            f.write(f"UID:{uid}\n")
            f.write(f"DTSTAMP:{dtstamp}\n")
            f.write(f"DTSTART:{dtstart}\n")
            f.write(f"DTEND:{dtend}\n")
            f.write(f"SUMMARY:{escaped_description}\n")
            f.write("END:VEVENT\n")

        # Write the calendar footer
        f.write("END:VCALENDAR\n")

    print(f"ICS file '{filename}' created successfully.")

def main():
    input_filename = "/Users/ssnipro/kitchen/a/output.txt"
    output_filename = 'output.ics'
    events = []

    # Read and parse the input file
    try:
        with open(input_filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:  # Skip empty lines
                    parsed = parse_event_line(line)
                    if parsed:
                        events.append(parsed)
    except FileNotFoundError:
        print(f"Input file '{input_filename}' not found.")
        return

    if not events:
        print("No valid events found to convert.")
        return

    # Create the ICS file
    create_ics(events, output_filename)

if __name__ == "__main__":
    main()
