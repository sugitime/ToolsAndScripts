#!/usr/bin/python3
from optparse import OptionParser
import os, time
import concurrent.futures


def runDirb(url, wordlist, outdir):
    if wordlist != False:
        os.system("dirb " + url + " " + wordlist + " -o " + outdir + "/" 
+ url.replace("http://", "").replace("https://", "").replace(":","."))
    else:
        os.system("dirb " + url + " -o " + outdir + "/" + 
url.replace("http://", "").replace("https://", "").replace(":","."))

if __name__=="__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", help="input 
file")
    parser.add_option("-d", "--directory", 
default=os.path.dirname(os.path.abspath(__file__)) + 
time.strftime("%j-%m-%y_%H:%M:%S"), dest="directory", help="output 
directory")
    parser.add_option("-w", "--wordlist", default=False, 
dest="wordlist", help="brute force wordlist")
    parser.add_option("-t", "--threads", default=32, dest="threads", 
help="number of threads")

    (options, args) = parser.parse_args()

    if options.filename == None:
        parser.print_help()
        exit()

    with open(options.filename) as f:
        content = f.readlines()
        executor = 
concurrent.futures.ProcessPoolExecutor(options.threads)
        futures = [executor.submit(runDirb, url, options.wordlist, 
options.directory) for url in content]
        concurrent.futures.wait(futures)


