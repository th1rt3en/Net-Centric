import re

choice = raw_input("Choose the pattern you want to find\n"
                   "1. Content of html tag\n"
                   "2. IP address\n"
                   "3. Email address\n"
                   "4. Valid date\n"
                   "5. Floating point number\n"
                   "6. Username\n"
                   "7. Hex number\n"
                   "8. Valid URL\n"
                   "9. IU Student ID\n"
                   "10. Valid credit card number\n")

while True:
    if choice == "1":
        string = raw_input("Enter the string: ")
        result = re.findall(r"<(\w+)>(.*)</\1>", string)
        if len(result):
            print "Found %d match(es)" % len(result)
            for _ in result:
                print _[1]
        else:
            print "No match found"

    elif choice == "2":
        string = raw_input("Enter the string: ")
        result = re.findall(r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
                            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", string)
        if len(result):
            print "Found %d match(es)" % len(result)
            for _ in result:
                print ".".join(_)
        else:
            print "No match found"

    elif choice == "3":
        string = raw_input("Enter the string: ")
        result = re.findall(r"[a-zA-Z0-9_.-]+@(?:[a-zA-Z0-9]+\.)+[a-zA-Z]{2,3}", string)
        if len(result):
            print "Found %d match(es)" % len(result)
            for _ in result:
                print _
        else:
            print "No match found"

    elif choice == "4":
        string = raw_input("Enter the string: ")
        result = re.findall(r"(3[01]|[12][0-9]|[1-9])/"
                            r"(1[0-2]|[1-9])/"
                            r"(\d+)", string)
        if len(result):
            print "Found %d match(es)" % len(result)
            for _ in result:
                print "/".join(_)
        else:
            print "No match found"

    elif choice == "5":
        string = raw_input("Enter the string: ")
        result = re.findall(r"\d+\.\d+", string)
        if len(result):
            print "Found %d match(es)" % len(result)
            for _ in result:
                print _
        else:
            print "No match found"

    elif choice == "6":
        string = raw_input("Enter the string: ")
        result = re.findall(r"[a-zA-Z0-9\-_]{3,16}", string)
        if len(result):
            print "Found %d match(es)" % len(result)
            for _ in result:
                print _
        else:
            print "No match found"

    elif choice == "7":
        string = raw_input("Enter the string: ")
        result = re.findall(r"[0-9a-fA-F]+", string)
        if len(result):
            print "Found %d match(es)" % len(result)
            for _ in result:
                print _
        else:
            print "No match found"

    elif choice == "8":
        string = raw_input("Enter the string: ")
        result = re.findall(r"(http|https)(://www)(\.[a-zA-Z0-9]+)*(\.[a-zA-Z0-9]+)(\.[a-zA-Z]{2,3})+", string)
        if len(result):
            print "Found %d match(es)" % len(result)
            for _ in result:
                print "".join(_)
        else:
            print "No match found"

    elif choice == "9":
        string = raw_input("Enter the string: ")
        result = re.findall(r"[A-Z]{6}\d{5}", string)
        if len(result):
            print "Found %d match(es)" % len(result)
            for _ in result:
                print _
        else:
            print "No match found"

    elif choice == "10":
        string = raw_input("Enter the string: ")
        result = re.findall(r"(4\d{12}|4\d{15})|"
                            r"(5[1-5]\d{14})|"
                            r"(3[47]\d{13})|"
                            r"6011\d{12}|65\d{14}", string)
        if len(result):
            print "Found %d match(es)" % len(result)
            for _ in result:
                print "".join(_)
        else:
            print "No match found"

    else:
        print "Invalid"
    choice = raw_input("Choose the pattern you want to find\n"
                       "1. Content of html tag\n"
                       "2. IP address\n"
                       "3. Email address\n"
                       "4. Valid date\n"
                       "5. Floating point number\n"
                       "6. Username\n"
                       "7. Hex number\n"
                       "8. Valid URL\n"
                       "9. IU Student ID\n"
                       "10. Valid credit card number\n")
