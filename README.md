# Operational Notes in Obsidian Generator

This project aims to help speed up some of the administrative elements of setting up for
a new operation. It's based on my own note-taking strategy using Obsidian, making use of 
plugins like DataView and internal file linking to quickly find information.

It might be overkill for some, I've tried to make it modular so you can customize the
templates to fit your needs (or add new templates). The extensibility gets harder if
there are things you want to find-and-replace as the program generates the folder - you'll
need to write your own replacement functions. I may move this into a class-based structure
later so you can just add a class.

# Structure and Methodology

If you want to see an example, open the `demo/` folder in Obsidian.

There are two supported layouts for the folder: internal and external. If you're doing a full
red team operation (starting outside the domain), use the **internal** layout, which is easier
to add in the external elements.

You can either initialze a full vault with this program, or add an individual op folder. See the
usage section for more, but for this section you should be aware of the layout:

```
OpName/
|--Content/
|--Images/
|--OpName-Tracker
|--OpName-Finding
|--OpName-DomainInfo (Internal Layout)
|--OpName-Canvas (Internal Layout)
```

`Content/` will hold all of your host and content notes, `Images/` is self explanatory. You can
easily link the files where needed, this is just to keep things tidy.

The `OpName-Tracker` file has some frontmatter about the op in general, a section for 
pertinent links (e.g., Jira), notes for kickoff and general operational notes, a section
to keep a to-do list, and then some optional sections that use DataView to query the host
notes for metadata. Currently, this is more useful for external ops where you'll have
more port/service information, but you can extend this with your own metadata.

The `OpName-Findings` file is where I keep all of my findings, using the template insertion
to quickly add a little section with a heading, details, and images section. You can then 
reference the heading in the host note where you found the issue. For example:

Findings file:
```
# SQL Injection (appname)
Details:
Lorem ipsum...

Images:
![[sql-injection.png]]
```

Host file:
```
...
# Findings
![[OpName-Findings#SQL Injection (appname)]]
```

This keeps the findings in a central location rather than needing to hunt through hosts to find
them.


## Internal Layout Additions
The internal layout adds `OpName-DomainInfo` and `OpName-Canvas`. I typically put helpful
domain information (e.g., the primary DC's IP, compromised accounts) that I don't want to
have to go find again later. If you put each domain in an AD forest as a Heading 1, you can
then just reference the desired domain in the canvas.

The canvas is a really cool feature of Obsidian. Think of it like draw.io, but you can populate
it with the notes and images you're already taking by dragging the files into the canvas. I'll
lay out my attack path here by dragging in the host / behavior notes and connecting the nodes with
the "glue". E.g., a node for your patient zero connected to a server with a line labled creds
in a share with the share path, and drop the screenshot evidence below that.

## Host Notes
The repo currently contains two different flavors of host notes - internal and external. They contain
different frontmatter that may be useful, along with a few different headings. They can be tweaked
to your desires by modifying `templates/External-Host.md` or `templates/Internal-Host.md`. You can add
these hosts manually using the template insertion in Obsidian (just remember to link the host back to
the tracker file), or you can use this tool to parse a host list/gnmap file.

# Automating the Setup
Cutting to the chase, you can run the tool with the positional arguments `init` or `parse`, which do
exactly what they sound like they do.

## `init` - Adding a folder or vault

Example init scenarios

```bash
# Create a new vault for a single op
python .\vault-generator.py init -f /home/users/sc0tch/assessments -n DemoOp -t internal --vault

# Create a new vault for multiple ops
python .\vault-generator.py init -f /home/users/sc0tch/assessments -n DemoOp -t internal --vault --reusable

# Add a new op to an existing vault
python .\vault-generator.py init -f /home/users/sc0tch/assessments/AssessmentNotes -n DemoOp2 -t external
```

`init` with only the required arguments (folder, op name, and op type) will create an op folder
in the target location. This is useful for existing vaults (your own, or a prior run).

You can optionally create a vault with `--vault`, which will use the op name as the vault name,
or use `--vault --reusable` to create a vault called `AssessmentNotes` with an op folder within it.
Use the second option if you want to have multiple ops in the same vault. This will use the contents
of `templates/obsidian` to set up some vault settings. If you have your own Obsidian settings, just
copy that into the vault or `templates/obsidian`. I recommend adding the DataView plugin back in,
and grab the contents of `types.json` and add it to your `types.json` to support the frontmatter.

If you already have a vault you want to use, you can use `--template` to create the template folder within
the op folder (i.e., `vault/OpName/01-Templates`).

```
usage: vault-generator.py init [-h] -f FOLDER -n NAME -t {internal,external} [--vault] [--reusable] [--template]

options:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        REQUIRED - The full path to the folder where you want the folder or vault created. NOTE 1: If
                        you already have a vault, give the vault folder path to put this in the root of the vault, or
                        designate one of the subfolders you have (e.g. vault/assessments). NOTE 2: This will NOT
                        create a templates folder, presuming you already have one. Add --template if you'd like a
                        template folder placed in the operation folder to copy out.
  -n NAME, --name NAME  REQUIRED - The operation codename.
  -t {internal,external}, --type {internal,external}
                        REQUIRED - The operation type: internal or external
  --vault               Creates an entire vault rather than a simple folder, using the op name for the vault folder
                        name. Will create the op folder and 01-Templates. Set your Obsidian settings to use
                        01-Templates as the template folder. Optional: replace the provided templates/obsidian folder
                        in this project with your with your own Obsidian settings. You will need at least the DataView
                        plugin installed and add the contents of types.json.
  --reusable            Use with --vault to create a vault structure to support multiple ops. Will instead name the
                        vault AssessmentNotes and create a sub-folder for the designated op. Other ops can then be
                        added by not supplying --vault in the future.
  --template            Creates a template folder in the operation folder without creating the whole vault.
```

## `parse` - Add host notes to an op folder from a host list or gnmap file
`parse` will accept one (or more) supplied files: a host list, a gnmap file, and/or a "host map" which
is a file providing `host,ip` for more specificity in naming the files. This is most useful for external
ops where you're doing broader enumeration vs. an internal where you probably won't touch all of the hosts.

**This presumes you have already initialized an op folder.**

The gnmap parsing will only pay attention to **open** ports and services. Once parsed, the ports/services will
be added to the frontmatter of the respective note. For best results, use the accompanying tool to create a map
file that will tie domains to IPs and feed that in as well, otherwise the host notes will likely only be named the IP.

The host list parsing will create templated notes, based on op type, with only the OpName filled in. You *can*
use the host list (`-l/--host-list`) flag with a gnmap file, but it's not recommended. I did not include logic
to look for files named `a.com` that match reverse DNS data from gnmap (e.g. `200.200.200.200 (a.com)`), so you'll likely
get duplicate files. If you plan to parse a gnmap, best to just ingore this flag altogether.

Example parse scenarios:
```bash
# Parse a gnmap file - host note named "IP (reverse dns from gnmap)"
python .\vault-generator.py parse -f /home/users/sc0tch/AssessmentNotes/DemoOp -n DemoOp -t internal -g client.gnmap

# Parse a gnmap file with a host map - host note named "domain.com (IP) (reverse dns from gnmap)"
python .\vault-generator.py parse -f /home/users/sc0tch/AssessmentNotes/DemoOp -n DemoOp -t internal -g client.gnmap -m client.hostmap

# Simply create notes from a scope list - host note named "domain.com"
python .\vault-generator.py parse -f /home/users/sc0tch/AssessmentNotes/DemoOp -n DemoOp -t internal -l client.scope
```

```
usage: vault-generator.py parse [-h] -f FOLDER -n NAME -t {internal,external} [-l HOST_LIST] [-g GNMAP] [-m HOST_MAP]

options:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        The full path to the operation folder. Expects that the folder has been initialized already
                        using the init command.
  -n NAME, --name NAME  REQUIRED - The operation codename.
  -t {internal,external}, --type {internal,external}
                        REQUIRED - The operation type: internal or external
  -l HOST_LIST, --host-list HOST_LIST
                        Path to the list of hosts, one per line. If you plan to use a gnmap file, you should use -g
                        and -m together instead of this option.
  -g GNMAP, --gnmap GNMAP
                        Path to the gnmap file to parse. Creates an Obsidian note per entry using the IP address and
                        reverse DNS name if available. Combine with -m to pair host name with IP.
  -m HOST_MAP, --host-map HOST_MAP
                        Path to a map file of format: host,ip with each host on a new line. Used to add host names to
                        file names instead of just IPs when parsing a gnmap file.
```

# Modifying Templates
Templates can be easily modified to suit your desires. Just find the appropriate markdown file in `templates/` and make
your changes. Files with `Op-XXXX` are the stock files that will get added to the root of an op folder, other files are
copied into `01-Templates` and used with the `parse` command.

To add a new template, simply create a markdown file and insert the file name (case sensitive) into the appropriate
global list in `vault-generator.py`. That array will get looped over during the respective actions.

## Harder modifications
Currently, the only text that gets replaced is "OpName", and parsed ports/services in the frontmatter. If you want
to replace other text on file creation, you'll need to add your own replacement function and call it in one
of the `write_X_X` functions.

If you want to parse other file types and add frontmatter, the `replace_frontmatter` function should work to insert it
into the right field in the template, but you'll need to add your own parser. I may break this program up into modules/classes
later to make this easier, but for now ¯\\_(ツ)_/¯.

# Domain to IP Map
Super rudimentary tool... the alarm wasn't working to change the timeout on `socket.gethostbyname()` so it's slow when a domain doesn't map to a live host. Might update this in the future to thread the requests, but this is just a simple way to create a csv of host,ip. Use something else if preferred.
