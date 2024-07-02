import os
import string
import sys
import io
import argparse
import shutil
import re

# To add your own templates, add a .md file to ./templates/ and then add the name here (case sensitive)
TEMPLATES = ["Finding.md", "External-Host.md", "Internal-Host.md", "Persona.md"]

# If you want certain files present when initializing an op, add a .md to ./templates/ 
# and add the name here (case sensitive)
# If you want to replace text that isn't OpName, you'll need to add your own replace_x function and call it
# in write_host_notes or write_stock_files
STOCK_FILES_ALL = ["Op-Findings.md", "Op-Tracker.md"]
STOCK_FILES_INTERNAL = ["Op-Canvas.canvas", "Op-DomainInfo.md"]

# Variable to hold file name:metadata mappings
# Typically of format {ip:{"rdns":gnmap_rdns, "domains":[], "ports":[], "services":[]}}
# Yes, I should have written this as a class
# If --host-list is intentionally supplied with --gnmap, the "ip" key will include domains without an ip
HOSTS = {}

#                 #
# Helpers Section #
#                 #

def validate_path(path):
    exists = False
    
    try:
        exists = os.path.exists(path)
    except Exception:
        pass

    return exists

def get_template_directory():
    """
    Gets the absolute path of where this script is running and appends /templates
    Works for Windows and Linux
    """
    # https://stackoverflow.com/a/404750
    if getattr(sys, 'frozen', False):
        app_path = os.path.dirname(sys.executable)
    elif __file__:
        app_path = os.path.dirname(__file__)

    template_path = os.path.join(app_path, "templates")

    return template_path

def create_directory(path, with_parent=False):
    if os.path.exists(path):
        return

    try:
        if with_parent:
            os.makedirs(path, exist_ok=True)
        else:
            os.mkdir(path)
    except Exception as e:
        raise Exception("Error creating folder at path {0}.\n\nError: {1}".format(path, e))

def get_file_contents(path):
    contents = ""
    try:
        with open(path, "r") as f:
            contents = f.read().splitlines()
    except Exception as e:
        raise Exception(e)

    return contents

def write_file(path, file_name, contents):
    file_path = os.path.join(path, file_name)
    try:
        with open(file_path, "w") as f:
            f.write("\n".join(contents))
    except Exception as e:
        print("Error writing to file: {0}.\n\nError: {1}".format(file_path, e))

def strip_domain(domain):
    domain = re.sub(r"https?://", "", domain.lower())
    domain = re.sub(r"/.*", "", domain)

    return domain

def replace_op_name(contents, op_name):
    updated_content = [sub.replace('OpName', op_name) for sub in contents]

    return updated_content

def replace_frontmatter(contents, data, field_name):
    """
    Takes a list of data, converts it to indented yaml, and inserts
    it at the designated field name in the template contents.
    """
    spacer = "  - "
    data_yaml = []
    insert_index = None
    new_contents = contents[:]
    
    # Generate appropriate yaml
    for item in data:
        data_yaml.append(spacer + "\"" + item + "\"")

    # Get the index to insert ports
    for i,line in enumerate(contents):
        if field_name in line:
            insert_index = i + 1
            break

    if insert_index is not None:
        new_contents[insert_index:insert_index] = data_yaml

    return new_contents


#              #
# Init section #
#              #
def handle_init(folder_path, op_name, op_type, is_new_vault, is_reusable, include_templates):
    
    # Get the respective paths
    # New, reusable vault for multiple ops. Does not use op name for vault name
    if is_new_vault and is_reusable:
        vault_path = os.path.join(folder_path,"AssessmentNotes")
        op_folder_path = os.path.join(vault_path, op_name)

    # New vault, but for single op. Uses op name as vault name
    elif is_new_vault:
        vault_path = os.path.join(folder_path, op_name)
        op_folder_path = vault_path

    # Simply add an op folder to an existing vault
    else:
        vault_path = folder_path
        op_folder_path = os.path.join(vault_path, op_name)

    template_folder_path = os.path.join(vault_path, "01-Templates")

    # Do a quick check to see if this op already exists
    if os.path.exists(op_folder_path):
        print("\n[!] WARNING: The supplied op name and folder already exists. This will overwrite the contents of "
            + "that folder. Do you want to continue?", end="(y/N): ")
        user_input = input()
        if user_input.lower() != 'y':
            print("Exiting.")
            sys.exit(1)

    # Create the vault structure if desired, otherwise just the folder
    if is_new_vault:
        create_vault(vault_path, op_folder_path, template_folder_path)
    else:
        try:
            create_directory(op_folder_path)
        except Exception as e:
            print(e)
            print("[!] Fatal - Exiting.")
            sys.exit(1)

        if include_templates:
            add_template_folder(op_folder_path + "/01-Templates")

    # Add the sub folders inside the new op
    try:
        create_directory(os.path.join(op_folder_path,"Content"))
        create_directory(os.path.join(op_folder_path,"Images"))
    except Exception as e:
        print(e)
        print("[!] Please create Vault/OpName/Content and Vault/OpName/Images before attempting to use the parse command.\n")
        sys.exit(1)

    # Add the starting files with appropriate names
    write_stock_files(op_folder_path, op_name, op_type)

def create_vault(vault_path, op_folder_path, template_folder_path):
    # Creates the vault and op folder together if the vault is reusable
    try:
        create_directory(op_folder_path, True)
        create_directory(template_folder_path)
    except Exception as e:
        print(e)
        print("[!] Fatal. Please check the folder path / permissions, clean things up, and try again.")
        sys.exit(1)

    copy_templates(template_folder_path)
    copy_obsidian_dir(vault_path)

def add_template_folder(template_folder_path):
    try:
        create_directory(template_folder_path)
    except Exception as e:
        print(e)
        print("[!] Please manually copy the templates folder into 01-Templates in your vault, or check "
            + "permissions and try again")
    copy_templates(template_folder_path)

def copy_obsidian_dir(vault_path):
    source_path = os.path.join(get_template_directory(),"obsidian")
    dest_path = os.path.join(vault_path,".obsidian")

    # See if it exists first. copytree won't overwrite so it needs to be removed
    if (os.path.exists(dest_path)):
        print("[!] WARNING: The .obsidian folder already exists in this vault. Skipping this. "
            + "This might mean you'll be missing some settings, like template folder location.")
        return

    try:
        shutil.copytree(source_path, dest_path)
    except Exception as e:
        print("Error copying obsidian directory to vault.\n\nError: {0}".format(e))

def copy_templates(template_folder_path):
    global TEMPLATES
    fresh_template_path = get_template_directory()

    for template in TEMPLATES:
        source_path = os.path.join(fresh_template_path, template)
        dest_path = os.path.join(template_folder_path, template)
        try:
            shutil.copy(source_path, dest_path)
        except Exception as e:
            print("Error copying template(s): {0}".format(e))


def write_stock_files(op_folder_path, op_name, op_type):
    global STOCK_FILES
    global STOCK_FILES_INTERNAL
    stock_files_path = get_template_directory()


    for file in STOCK_FILES_ALL:
        source_path = os.path.join(stock_files_path, file)
    
        try:
            contents = get_file_contents(source_path)
        except Exception as e:
            print("[!] Error fetching contents of stock file: {0}\nError: {1}".format(file, e))
    
        replaced_text = replace_op_name(contents, op_name)
        file_name = file.replace("Op", op_name)
        write_file(op_folder_path, file_name, replaced_text)

    if op_type == "internal":
        for file in STOCK_FILES_INTERNAL:
            source_path = os.path.join(stock_files_path, file)

            try:
                contents = get_file_contents(source_path)
            except Exception as e:
                print("[!] Error fetching contents of stock file: {0}\nError: {1}".format(file, e))

            replaced_text = replace_op_name(contents, op_name)
            file_name = file.replace("Op", op_name)
            write_file(op_folder_path, file_name, replaced_text)

        # Stage a patient zero (witting click or initial access)
        source_path = os.path.join(stock_files_path, "Internal-Host.md")

        try:
            contents = get_file_contents(source_path)
        except Exception as e:
            print("[!] Error fetching contents of stock file: {0}\nError: {1}".format(file, e))
    
        replaced_text = replace_op_name(contents, op_name)
        write_file(os.path.join(op_folder_path, "Content"), "Patient-Zero.md", replaced_text)


#               #
# Parse section #
#               #
def is_initialized(path):
    initialized = False
    tracker = False
    content_folder = False
    
    if not validate_path(path):
        print("Error: supplied folder ({0}) not found. Please run init and/or check that the path is correct.".format(path))
        return initialized
        
    folder_contents = [item.path for item in os.scandir(path)]

    for item in folder_contents:
        if "tracker" in os.path.basename(item).lower():
            tracker = True
        if "content" in os.path.basename(item).lower():
            content_folder = True

    if tracker and content_folder:
        initialized = True

    return initialized


def handle_parse(folder_path, op_name, op_type, host_list_path, gnmap_path, host_map_path):
    gnmap_present = False

    # Figure out which one(s) of these exists
    if host_list_path is not None:
        if not validate_path(host_list_path):
            print("Error: The supplied host-list could not be found: {0}".format(host_list_path))
            sys.exit(1)
        parse_host_list(host_list_path)

    if gnmap_path is not None:
        if not validate_path(gnmap_path):
            print("Error: The supplied gnmap file could not be found: {0}".format(gnmap))
            sys.exit(1)
        gnmap_present = True
        parse_gnmap(gnmap_path)

    if host_map_path is not None:
        if not validate_path(host_map_path):
            print("Error: The supplied host-map could not be found: {0}".format(host_map_path))
            sys.exit(1)
        parse_host_map(host_map_path, gnmap_present)

    write_host_notes(folder_path, op_name, op_type)

def write_host_notes(folder_path, op_name, op_type):
    global HOSTS
    content_folder = os.path.join(folder_path, "Content")
    template_path = get_template_directory()

    # Get the right template
    if op_type.lower() == "internal":
        template_path = os.path.join(template_path, "Internal-Host.md")
    else: 
        template_path = os.path.join(template_path, "External-Host.md")

    # Get clean copies of the templates
    fresh_contents = []
    try:
        fresh_contents = get_file_contents(template_path)
    except Exception as e:
        print(e)
        print("[!] Error fetching template contents ({0}) - Fatal. Exiting.".format(template_path))
        sys.exit(1)

    for host in HOSTS:
        # Don't muck up the clean copies with find/replace
        contents = fresh_contents[:]

        contents = replace_op_name(contents, op_name)
        file_name = ""
        
        # Handle non-IP entries from host-list
        if not re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", host):
            file_name = host + ".md"
            write_file(content_folder, file_name, contents)
            continue

        # Grab common values
        rdns = HOSTS[host]["rdns"]
        if len(HOSTS[host]["ports"]) != 0:
            contents = replace_frontmatter(contents, HOSTS[host]["ports"], "openPorts")
        if len(HOSTS[host]["services"]) != 0:
            contents = replace_frontmatter(contents, HOSTS[host]["services"], "services")

        # Separate hosts with no domain vs. ones with domain(s)
        if len(HOSTS[host]["domains"]) == 0:
            if rdns == '()':
                file_name = host + " ().md"
            else:
                file_name = host + " " + rdns + ".md"
            write_file(content_folder, file_name, contents)
        else:
            for domain in HOSTS[host]["domains"]:
                if rdns == '()':
                    file_name = domain + " - (" + host + ").md"
                else:
                    file_name = domain + " - (" + host + ") " + rdns + ".md"

                write_file(content_folder, file_name, contents)


def parse_host_list(host_list_path):
    global HOSTS
    try:
        host_list = get_file_contents(host_list_path)
    except Exception as e:
        print("[!] Error fetching contents of host list. Error: {0}".format(e))
        return

    for host in host_list:
        host = strip_domain(host)
        HOSTS[host] = {"rdns": "", "domains":[host], "ports": [], "services": []}


def parse_gnmap(gnmap_path):
    global HOSTS
    try:
        contents = get_file_contents(gnmap_path)
    except Exception as e:
        print("[!] Error fetching contents of gnmap file. Error: {0}".format(e))
        return

    for line in contents:
        # Skip lines that don't have open ports to parse
        if not ("host" and "/open/" in line.lower()):
            continue

        # Get the sections of the gnmap that are useful as arrays
        host_info = line.split('\t')[0].split(' ')
        ports_info = line.split('\t')[1][7:].split(', ')

        # Get the IP and rdns (if available)
        ip = host_info[1]
        rdns = host_info[2]

        # Loop over the port strings and add # and services
        host_ports = []
        host_services = []
        for port in ports_info:

            if not "/open/" in port.lower():
                continue

            port_num, state, proto, owner, service, rpc, version, empty = port.split("/")

            host_ports.append(port_num)

            if service != "" and not service in host_services:
                host_services.append(service)

            # Create the dict entry
            HOSTS[ip] = {"rdns": rdns, "domains":[], "ports": host_ports, "services":host_services}


def parse_host_map(host_map_path, gnmap_present):
    global HOSTS
    try:
        host_pairs = get_file_contents(host_map_path)
    except Exception as e:
        print("[!] Error fetching contents of host map file. Error: {0}".format(e))
        return

    domain_index = 0
    ip_index = 1

    # A little error handling for bad user input that flips host and IP
    test_str = host_pairs[1].split(",")
    if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", test_str[0]):
        domain_index = 1
        ip_index = 0

    for host in host_pairs:
        ip = ""
        domain = ""
        try:
            temp_arr = host.split(",")
            domain = temp_arr[domain_index]
            ip = temp_arr[ip_index]
        except IndexError as e:
            print("[*] Missing full pair for {0} in host map. Skipping.".format(temp_arr[0]))
            continue

        domain = strip_domain(domain)
        if ip in HOSTS:
            HOSTS[ip]["domains"].append(domain)
        elif not gnmap_present:
            # Only add hosts not already in the dict if there wasn't a gnmap parsed
            # Avoids adding hosts without any open ports
            HOSTS[ip] = {"rdns":"", "domains":[domain],"ports":[],"services":[]}



def main():
    parser = argparse.ArgumentParser(description="A program to quickly set up notes for an operation.")
    subparsers = parser.add_subparsers(dest="command")

    # Assessment init
    parser_init = subparsers.add_parser( "init", help="Initialize an assessment folder or vault at the target location")
    parser_init.add_argument("-f", "--folder", required=True, help="REQUIRED - The full path to the folder where you "
                    + "want the folder or vault created. "
                    + "NOTE 1: If you already have a vault, give the vault folder path to put this in the root of the vault, "
                    + "or designate one of the subfolders you have (e.g. vault/assessments). "
                    + "NOTE 2: This will NOT create a templates folder, presuming you already have one. Add "
                    + "--template if you'd like a template folder placed in the operation folder to copy out.")
    parser_init.add_argument("-n", "--name", required=True, help="REQUIRED - The operation codename.")
    parser_init.add_argument("-t", "--type", required=True, help="REQUIRED - The operation type: internal or external",
                             choices=["internal", "external"], type=str.lower)
    parser_init.add_argument("--vault", help="Creates an entire vault rather than a simple folder, using the op name for the "
                    + "vault folder name. Will create the op folder and 01-Templates. Set your Obsidian settings to use "
                    + "01-Templates as the template folder. Optional: replace the provided templates/obsidian folder in "
                    + "this project with your with your own Obsidian settings. You will need at least the DataView "
                    + "plugin installed and add the contents of types.json.",
                    action="store_true")
    parser_init.add_argument("--reusable", help="Use with --vault to create a vault structure to support multiple ops. Will "
                    + "instead name the vault AssessmentNotes and create a sub-folder for the designated op. Other ops can "
                    + "then be added by not supplying --vault in the future.", action="store_true")
    parser_init.add_argument("--template", help="Creates a template folder in the operation folder without creating the "
                    + "whole vault.", action="store_true")

    # Host parse
    parser_parse = subparsers.add_parser("parse", help="Parse a supplied gnmap or host list into Obsidian notes. Requires an "
                    + "initialized op folder using the init command.")
    parser_parse.add_argument("-f", "--folder", help="The full path to the operation folder. Expects that the folder has "
                    + "been initialized already using the init command.", required=True)
    parser_parse.add_argument("-n", "--name", required=True, help="REQUIRED - The operation codename.")
    parser_parse.add_argument("-t", "--type", required=True, help="REQUIRED - The operation type: internal or external",
                             choices=["internal", "external"], type=str.lower)
    parser_parse.add_argument("-l", "--host-list", help="Path to the list of hosts, one per line. If you plan to use "
                    + "a gnmap file, you should use -g and -m together instead of this option.")
    parser_parse.add_argument("-g", "--gnmap", help="Path to the gnmap file to parse. Creates an Obsidian note per entry "
                    + "using the IP address and reverse DNS name if available. Combine with -m to pair host name with IP.")
    parser_parse.add_argument("-m", "--host-map", help="Path to a map file of format: host,ip with each host on a new line. "
                    + "Used to add host names to file names instead of just IPs when parsing a gnmap file.")


    args = parser.parse_args()

    if args.command == "parse":
        if not is_initialized(args.folder):
            print("Error: The supplied folder does not appear to be initialized. Please run init first.")
            sys.exit(1)
        
        if args.host_list is None and args.gnmap is None and args.host_map is None:
            print("Error: Please supply at least one of: -l/--host-list, -g/--gnmap, -m/--host-map to continue.")
            sys.exit(1)

        if args.host_list and args.host_map:
            print("[*] You supplied both a host list and host map, defaulting to host map for file creation.\n")
            args.host_list = None

        if args.host_list and args.gnmap:
            print("\n[!] You have supplied both a host list and a gnmap file. I can (A) create files for both, which "
                + "may result in duplicate host files; (B) only use the gnmap (and map file, if supplied); or (C) "
                + "terminate and you combine the host and IP list into a file with format host,ip on new lines "
                + "before running again with -g and -m. Which would you like to do? ", end="(a/b/C): ")
            user_input = input()
            match user_input.lower():
                case "b":
                    args.host_list = None
                case "c":
                    print("Exiting.")
                    sys.exit(1)
                case _:
                    pass

        handle_parse(args.folder, args.name, args.type, args.host_list, args.gnmap, args.host_map)
        print('[+] If you already have this vault open, the DataView tables might not work until you '
            + 're-open the vault.')

    if args.command == "init":
        # Validate the path
        if validate_path(args.folder):
            handle_init(args.folder, args.name, args.type, args.vault, args.reusable, args.template)
        else:
            print("The designated path does not exist. Please supply an existing folder in which to create the vault / op folder.\n\n"
                  + "Example: /home/users/demoUser/ for a vault or /home/users/demoUser/AssessmentNotes for a single op folder")
            sys.exit(1)

        print("\n[+] Your repo is ready. If you already have it open, it should refresh. If it's new, Go to Obsidian > "
            + "Manage Vaults > Open Folder as Vault.\n\n")
        print("A few reminders:"
            + "\n\n\t- If you used --vault and --reusable, don't use those again next time to just\n\t  add a folder to the vault"
            + "\n\n\t- Templates can be modified/added in the project folder for the future, some more \n\t  easily than others. "
            + "The hardest modifications would be adding more\n\t  find-and-replace values, otherwise the markdown "
            + "can be changed at will."
            + "\n\n\t- Use the 'parse' command to parse a host list, gnmap file, or gnmap file + host,ip \n\t  map file "
            + "to populate notes in your new repo with the parse command\n")
    

if __name__ == "__main__":
    main()