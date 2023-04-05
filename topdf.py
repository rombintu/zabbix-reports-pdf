import os, random
import shutil
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib import rcParams
from zapi import Host

rcParams['axes.spines.top'] = False
rcParams['axes.spines.right'] = False

WORK_DIR = os.getcwd()
PLOT_DIR = os.path.join(WORK_DIR, 'plots')
REPORT_DIR = os.path.join(WORK_DIR, 'reports')
REPORT_FILE_NAME = "report_{}.pdf"

def randcolor():
    r = lambda: random.randint(0,255)
    return '#%02X%02X%02X' % (r(),r(),r())


def plot(data_list: tuple[str, str, pd.DataFrame], filename: str, hostname: str):
    plt.figure(figsize=(12, 4))
    plt.grid(color='#F2F2F2', alpha=1, zorder=0)
    for label, predata, data in data_list:
        plt.plot(data['Date'], data['Values'], color=randcolor(), lw=1, zorder=5, label=label)
        plt.figtext(x=0.3, y=-1, s=predata)
    plt.title(hostname, fontsize=17)
    plt.xlabel('Period', fontsize=13)
    plt.xticks(fontsize=9)
    plt.ylabel('CPU Utilization', fontsize=13)
    plt.yticks(fontsize=9)
    plt.legend()
    plt.savefig(filename, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close()
    return
              
def generate_df_from_data(item_name, item_predata, timestamps, values) -> pd.DataFrame:
    return (item_name, item_predata, pd.DataFrame({
        'Date': timestamps,
        'Values': values
    }))

def construct(hosts: list[Host]):
    # Delete folder if exists and create it again
    try:
        shutil.rmtree(PLOT_DIR)
        os.mkdir(PLOT_DIR)
    except FileNotFoundError:
        os.mkdir(PLOT_DIR)
        
    
    for host in hosts:
        data_list = []
        predata = ""
        for item in host.items:
            predata += "\n" + item.predata
        for item in host.items:
            data_list.append(generate_df_from_data(item.name, predata, item.timestamps, item.values))
        plot(
            data_list=data_list,
            filename=os.path.join(PLOT_DIR, f'{host.filename}_{item.itemid}.png'),
            hostname=host.name
        )
    counter = 0
    pages_data = []
    temp = []
    # Get all plots
    files = os.listdir(PLOT_DIR)
    # files = sorted(os.listdir(PLOT_DIR), key=lambda x: int(x.split('.')[0]))
    for fname in files:
        if counter == 3:
            pages_data.append(temp)
            temp = []
            counter = 0

        temp.append(os.path.join(PLOT_DIR, fname))
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
        self.cell(60, 1, 'Zabbix reports PDF', 0, 0, 'R')
        self.ln(20)
        
    def footer(self):
        # Page numbers in the footer
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

    def page_body(self, img):
        # if len(images) == 3:
        #     self.image(images[0], 15, 25, self.WIDTH - 30)
        #     self.image(images[1], 15, self.WIDTH / 2 + 5, self.WIDTH - 30)
        #     self.image(images[2], 15, self.WIDTH / 2 + 90, self.WIDTH - 30)
        # elif len(images) == 2:
        #     self.image(images[0], 15, 25, self.WIDTH - 30)
        #     self.image(images[1], 15, self.WIDTH / 2 + 5, self.WIDTH - 30)
        # else:
        #     self.image(images[0], 15, 25, self.WIDTH - 30)
        self.image(img, 15, 25, self.WIDTH - 30)
            
    def print_page(self, images):
        # Generates the report
        for img in images:
            self.add_page()
            self.page_body(img)

