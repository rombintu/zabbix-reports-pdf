import os, sys
import shutil
import pandas as pd
from fpdf import FPDF
from zapi import Zapi
import matplotlib.pyplot as plt
from matplotlib import rcParams
from datetime import datetime

import argparse

rcParams['axes.spines.top'] = False
rcParams['axes.spines.right'] = False

WORK_DIR = os.getcwd()
PLOT_DIR = os.path.join(WORK_DIR, 'plots')
REPORT_DIR = os.path.join(WORK_DIR, 'reports')
REPORT_FILE_NAME = "report_{}.pdf"

def plot(data: pd.DataFrame, filename: str):
    plt.figure(figsize=(12, 4))
    plt.grid(color='#F2F2F2', alpha=1, zorder=0)
    plt.plot(data['Date'], data['Values'], color='#087E8B', lw=1, zorder=5)
    plt.title('Monitor stats', fontsize=17)
    plt.xlabel('Period', fontsize=13)
    plt.xticks(fontsize=9)
    plt.ylabel('CPU Utilization', fontsize=13)
    plt.yticks(fontsize=9)
    plt.savefig(filename, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close()
    return
              
def generate_df_from_data(timestamps, values) -> pd.DataFrame:
    return pd.DataFrame({
        'Date': timestamps,
        'Values': values
    })



def construct(hosts):
    # Delete folder if exists and create it again
    try:
        shutil.rmtree(PLOT_DIR)
        os.mkdir(PLOT_DIR)
    except FileNotFoundError:
        os.mkdir(PLOT_DIR)
        
    
    for host in hosts:
        # Save visualization
        for i, (timestamps, values) in enumerate(host["dataitems"]):
            plot(data=generate_df_from_data(
                    timestamps,values),
                filename=os.path.join(PLOT_DIR, f'{host["_id"]}_{i}.png'))
    # plot(data=generate_data(), filename=f'{PLOT_DIR}/{0}.png')
    # Construct data shown in document
    counter = 0
    pages_data = []
    temp = []
    # Get all plots
    files = os.listdir(PLOT_DIR)
    # Sort them by month - a bit tricky because the file names are strings
    files = sorted(os.listdir(PLOT_DIR), key=lambda x: int(x.split('.')[0]))
    # Iterate over all created visualization
    for fname in files:
        # We want 3 per page
        if counter == 3:
            pages_data.append(temp)
            temp = []
            counter = 0

        temp.append(f'{PLOT_DIR}/{fname}')
        counter += 1

    return [*pages_data, temp]

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.WIDTH = 210
        self.HEIGHT = 297
        
    def header(self):
        # Custom logo and positioning
        # Create an `assets` folder and put any wide and short image inside
        # Name the image `logo.png`
        # self.image('assets/logo.png', 10, 8, 33)
        self.set_font('Arial', 'B', 11)
        self.cell(self.WIDTH - 80)
        self.cell(60, 1, 'CPU', 0, 0, 'R')
        self.ln(20)
        
    def footer(self):
        # Page numbers in the footer
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def page_body(self, images):
        # Determine how many plots there are per page and set positions
        # and margins accordingly
        if len(images) == 3:
            self.image(images[0], 15, 25, self.WIDTH - 30)
            self.image(images[1], 15, self.WIDTH / 2 + 5, self.WIDTH - 30)
            self.image(images[2], 15, self.WIDTH / 2 + 90, self.WIDTH - 30)
        elif len(images) == 2:
            self.image(images[0], 15, 25, self.WIDTH - 30)
            self.image(images[1], 15, self.WIDTH / 2 + 5, self.WIDTH - 30)
        else:
            self.image(images[0], 15, 25, self.WIDTH - 30)
            
    def print_page(self, images):
        # Generates the report
        self.add_page()
        self.page_body(images)

if __name__ == "__main__":

    pars = argparse.ArgumentParser()
    pars.add_argument("--url", help="Zabbix url (http://zabbix.com:8080)")
    pars.add_argument("--token", help="Zabbix token")
    args = pars.parse_args()

    url = args.url
    token = args.token
    if not url or not token:
        print("--url or --token is None. Use --help")
        sys.exit(0)

    pdf = PDF()
    zapi = Zapi(
        url = args.url, 
        token = args.token,
        ssl=False,
    )
    hosts = zapi.get_itemids_and_hostid(host_names=["dev0", "Zabbix server"])
    history_hosts = zapi.get_history_all_host(hosts)
    for elem in construct(history_hosts):
        pdf.print_page(elem)
    
    try:
        os.mkdir(REPORT_DIR)
    except FileExistsError:
        print(f"Dir {REPORT_DIR} already exists")

    pdf.output(os.path.join(REPORT_DIR, REPORT_FILE_NAME.format(datetime.now().strftime("%d%m%y"))), 'F')