from pyzabbix import ZabbixAPI
from datetime import datetime, timedelta
from statistics import mean

class Item:
    def __init__(self, name, itemid):
        self.name = name 
        self.itemid = itemid
        self.items_predata = {
            "last": None,
            "min": None,
            "max": None,
            "avg": None, 
        }
        self.history = {
            "timestamps": [],
            "values": []
        }
        # self.timestamps = []
        # self.values = []

    def set_timestamps(self, timestamps):
        self.history["timestamps"] = timestamps

    def set_predata(self, last, min, max, avg):
        self.items_predata["last"] = last
        self.items_predata["min"] = min
        self.items_predata["max"] = max
        self.items_predata["avg"] = avg

    @property
    def predata(self):
        return f"""{self.name} (last, min, max, avg)
        {self.items_predata['last']}% \
        {self.items_predata['min']}% \
        {self.items_predata['max']}% \
        {self.items_predata['avg']}%"""

    @property
    def timestamps(self):
        return self.history["timestamps"]
    
    def set_values(self, values):
        self.history["values"] = values
    @property
    def values(self):
        return self.history["values"]

class Host:
    def __init__(self, name):
        self.hostid = ""
        self.name = name
        self.filename = "_".join(name.split())
        self.items_data = {
            "items": []
        }

    @property
    def items(self):
        return self.items_data["items"]
    
    def add_item(self, item: Item):
        self.items_data["items"].append(item)
    def set_hostid(self, hostid):
        self.hostid = hostid


class ZabbixCollector:
    
    def add_host(self, host):
        self.hosts_data["hosts"].append(host)

    def __init__(self, url, token, ssl=False, hostnames=[]):
        self.api = ZabbixAPI(url)
        self.api.session.verify = ssl
        self.api.login(api_token=token)
        print("Connected to Zabbix api Version %s" % self.api.api_version())

        self.hosts_data = {
            "hosts": []
        }

        for hostname in hostnames:
            self.add_host(Host(name=hostname))

    @property
    def hosts(self):
        return self.hosts_data["hosts"]
    

    def collect_items_by_key(self, key="system.cpu.util"):
        for host in self.hosts:
            items = self.api.item.get(
                output="extend",
                search={"key_": key},
                host=host.name,
            )
            if not items:
                print(f"No data for {host.name}")
                continue
            host.set_hostid(items[0]["hostid"])
            for item in items:
                host.add_item(Item(itemid=item['itemid'], name=item['name']))
        return
    
        
    def collect_history(self):
        for host in self.hosts:
            for item in host.items:
                history = self.api.history.get(
                    output="extend", 
                    hostids=host.hostid, 
                    history=0, 
                    sortorder='ASC', 
                    sortfield="clock", 
                    itemids=item.itemid, 
                    time_from=int((datetime.now() - timedelta(days=1)).timestamp()),
                )
                if not history:
                    print(f"No history for {host.name}: {item.name}")
                    continue
                timestamps = []
                values = []
                for h in history:
                    timestamps.append(datetime.fromtimestamp(int(h['clock'])))
                    values.append(float(h['value']))
                item.set_timestamps(timestamps)
                item.set_values(values)
                item.set_predata(
                    round(values[-1], 4), 
                    round(min(values), 4), 
                    round(max(values), 4), 
                    round(mean(values), 4))
        return
    
    def run(self):
        self.collect_items_by_key()
        self.collect_history()