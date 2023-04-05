import argparse, sys, os
from datetime import datetime
from topdf import PDF, construct
from topdf import REPORT_DIR, REPORT_FILE_NAME
from zapi import ZabbixCollector

from urllib3 import exceptions
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=exceptions.InsecureRequestWarning)

if __name__ == "__main__":

    pars = argparse.ArgumentParser()
    pars.add_argument("--url", help="Zabbix url (http://zabbix.com:8080)")
    pars.add_argument("--token", help="Zabbix token")
    pars.add_argument("--host", help="Hostname of host from zabbix server/agent")
    args = pars.parse_args()

    url = args.url
    token = args.token
    host = args.host
    if not url or not token or not host:
        print("--url or --token or --host is None. Use --help")
        sys.exit(0)

    pdf = PDF()
    zapi = ZabbixCollector(
        url = url, 
        token = token,
        ssl=False,
        hostnames=[host]
    )
    zapi.run()
    for elem in construct(zapi.hosts):
        pdf.print_page(elem)
    
    try:
        os.mkdir(REPORT_DIR)
    except FileExistsError:
        print(f"Dir {REPORT_DIR} already exists")

    pdf.output(os.path.join(REPORT_DIR, REPORT_FILE_NAME.format(datetime.now().strftime("%d%m%y"))), 'F')