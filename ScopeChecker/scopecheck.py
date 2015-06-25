#!/usr/bin/python
from optparse import OptionParser
import os, time, socket, sys, re
#some import checks...
try:
    import netaddr
except ImportError as error:
    print "Please install netaddr.\r\npip install netaddr\r\n\r\nIf pip is not installed, install pip\r\nhttps://pip.pypa.io/en/latest/installing.html"
    exit()
try:
    import concurrent.futures
except ImportError as error:
    print "Please install concurrent.futures.\r\npip install futures\r\nIf pip is not installed, install pip\r\nhttps://pip.pypa.io/en/latest/installing.html"
    exit()

def ip_compare(ip_addr, scope_list):
    ip_addr = ip_addr.rstrip()
    if not is_ipv4(ip_addr):
        try:
            ip = socket.gethostbyname(ip_addr)
        except:
            return "error," + ip_addr + ",,," + str(sys.exc_info()[0]).replace(',',';') + "\r\n"
    else:
        ip = ip_addr
    for scope in scope_list:
        if netaddr.IPAddress(ip) in netaddr.IPNetwork(scope):
            return "in," + ip_addr + "," + ip + "," + scope + ",\r\n"
    return "out," + ip_addr + "," + ip + "," + ",,\r\n"

def is_ipv4(ip):
    match = re.match("^(\d{0,3})\.(\d{0,3})\.(\d{0,3})\.(\d{0,3})$", ip)
    if not match:
        return False
    quad = []
    for number in match.groups():
        quad.append(int(number))
    if quad[0] < 1:
        return False
    for number in quad:
        if number > 255 or number < 0:
            return False
    return True

def is_valid_file(arg):
    if not os.path.exists(arg):
        return False
    else:
        return True

if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", help="file of ip's to check")
    parser.add_option("-s", "--scopelist", default=False, dest="scopelist", help="file containing scope subnets")
    parser.add_option("-o", "--outputfile", default=os.path.dirname(os.path.abspath(__file__)) + "\\" + "Scope-Check-" + time.strftime("%j-%m-%y_%H:%M:%S") + ".csv", dest="outputfile", help="output directory")
    parser.add_option("-t", "--thread-speed", default="medium", dest="threadspeed", help="speed of scan\r\n--low - 8 threads\r\n--medium - 16 threads\r\n--fast - 32 threads\r\n--#yolo - 64 threads")
    (options, args) = parser.parse_args()

    if not options.filename or not options.scopelist:
        parser.print_help()
        exit()

    if not is_valid_file(options.filename or not is_valid_file(options.scopelist)):
        print "Error: Invalid list of IP's or scope list."
        exit()
    #set thread speed. I could have just done -t [int] but I had to give the 'yolo' option, so, ya know...
    thread_options = {
        'low':8,
        'medium':16,
        'fast':32,
        '#yolo':64
    }
    threads = thread_options[options.threadspeed]

    scope_file = open(options.scopelist, 'r')
    scope_list = scope_file.readlines()

    output = ["status,hostname,ip,scope,error\r\n"]

    with open(options.filename) as f:
        contents = f.readlines()
        executor = concurrent.futures.ProcessPoolExecutor(threads)
        futures = [executor.submit(ip_compare, ip, scope_list) for ip in contents]
        #concurrent.futures.wait(futures)

    for future in concurrent.futures.as_completed(futures):
        try:
            output.append(future.result())
        except:
            pass

    outfile = open(options.outputfile, 'w')
    outfile.writelines(output)

    print "Done."
    exit()

