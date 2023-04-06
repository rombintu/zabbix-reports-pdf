import argparse, sys, os
from datetime import datetime
from images import PDF, construct
from images import REPORT_DIR, REPORT_FILE_NAME
from zapi import ZabbixCollector
from jinja2 import FileSystemLoader, Environment
from urllib3 import exceptions
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=exceptions.InsecureRequestWarning)

def read_hostfile(path: str):
    lines = []
    with open(path, "r") as f:
        for line in f.readlines():
            # Skip empty lines and comments
            if line == "" or line.startswith("#"): continue
            lines.append(line.strip())
    if not lines:
        print(f"Hostfile: {path} is empty")
        sys.exit(0)
    return lines

if __name__ == "__main__":

    pars = argparse.ArgumentParser()
    pars.add_argument("--url", help="Zabbix url (http://zabbix.com:8080)")
    pars.add_argument("--token", help="Zabbix token")
    pars.add_argument("--hostfile", help="Hostname of host from zabbix server/agent")
    args = pars.parse_args()

    url = args.url
    token = args.token
    hostfile = args.hostfile
    if not url or not token or not hostfile:
        print("--url or --token or --hostfile are None. Use --help")
        sys.exit(0)

    # pdf = PDF()
    zapi = ZabbixCollector(
        url = url, 
        token = token,
        ssl=False,
        hostnames=read_hostfile(hostfile)
    )
    zapi.run()
    # for elem in construct(zapi.hosts):
    #     pdf.print_page(elem)
    # imgs, tables = construct(zapi.hosts)
    try:
        os.mkdir(REPORT_DIR)
    except FileExistsError:
        print(f"Dir {REPORT_DIR} already exists")
    
    title = REPORT_FILE_NAME.format(datetime.now().strftime("%d%m%y"))
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('template.html')
    html = template.render(title=title, images=construct(zapi.hosts))
    # pdf.output(os.path.join(REPORT_DIR, REPORT_FILE_NAME.format(datetime.now().strftime("%d%m%y"))), 'F')

    with open(os.path.join(REPORT_DIR, f'{title}.html'), 'w') as f:
        f.write(html)