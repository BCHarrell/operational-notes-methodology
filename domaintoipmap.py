import argparse
import socket
from contextlib import contextmanager
import signal

def raise_error(signum, frame):
    """This handler will raise an error inside gethostbyname"""
    raise OSError

@contextmanager
def set_signal(signum, handler):
    """Temporarily set signal"""
    old_handler = signal.getsignal(signum)
    signal.signal(signum, handler)
    try:
        yield
    finally:
        signal.signal(signum, old_handler)

@contextmanager
def set_alarm(time):
    """Temporarily set alarm"""
    signal.setitimer(signal.ITIMER_REAL, time)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0) # Disable alarm

@contextmanager
def raise_on_timeout(time):
    """This context manager will raise an OSError unless
    The with scope is exited in time."""
    with set_signal(signal.SIGALRM, raise_error):
        with set_alarm(time): 
            yield

def read_file(filename):
	hosts = []
	try:
		with open(filename) as f:
			hosts = f.readlines()
	except Exception as e:
		print("Error reading input file: {0}".format(e))

	return hosts

def write_output(map, output_file, ip_file):
	try:
		with open(output_file, 'w') as m, open(ip_file, 'w') as i:
			for item in map:
				m.write(item["host"] + "," + item["ip"] + "\n")
				if item["ip"] != "":
					i.write(item["ip"] + "\n")
	except Execption as e:
		print("Error writing output: {0}".format(e))


def fetch_ips(hosts):
	mapping = []

	for host in hosts:	
		host = host.rstrip()
		print("Resolving host: {0}".format(host))
		try:
			with raise_on_timeout(1.5): # Timeout 1.5s
				s = socket.gethostbyname(host)
				mapping.append({"host": host, "ip": s})
		except:
			mapping.append({"host": host, "ip": ""})
			continue

	return mapping


def main():
	parser = argparse.ArgumentParser(prog="Parse hosts for ips", description="Output two files, one with hosts and IPs and one with just IPs")
	parser.add_argument('-i', '--input', help="Full path to the input file")
	parser.add_argument('-oM', '--map', help="Full path to the output file for subdomains")
	parser.add_argument('-oI', '--ips', help="Full path to the output file for IPs")

	args = parser.parse_args()

	if args.input is None or args.map is None or args.ips is None:
		print("Please supply the required arguments: -i INPUT.txt -oM OUTPUT_MAP.txt -oI OUTPUT_IP.txt")
		exit()

	hosts = read_file(args.input)
	mapping = fetch_ips(hosts)
	write_output(mapping, args.map, args.ips)


if __name__ == '__main__':
	main()