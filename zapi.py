from pyzabbix import ZabbixAPI
from datetime import datetime, timedelta

class Item:
    itemid: str
    name: str
    history: dict = {"timestamps": [], "values": []}

    def __init__(self, name, itemid):
        self.name = name 
        self.itemid = itemid

    def set_timestamps(self, timestamps):
        self.history["timestamps"] = timestamps
    def set_values(self, values):
        self.history["values"] = values

class Host:
    hostid: str
    name: str
    filename: str
    items: list[Item] = []

    def __init__(self, name):
        self.name = name
        self.filename = "_".join(name.split())

    def set_hostid(self, hostid):
        self.hostid = hostid

    def add_item(self, item: Item):
        self.items.append(item)


class ZabbixCollector:
    hosts: list[Host] = []

    def __init__(self, url, token, ssl=False, hostnames=[]):
        self.api = ZabbixAPI(url)
        self.api.session.verify = ssl
        self.api.login(api_token=token)
        print("Connected to Zabbix api Version %s" % self.api.api_version())

        for hostname in hostnames:
            self.hosts.append(Host(name=hostname))

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
                    print(f"Error for {host.name}")
                    return
                timestamps = []
                values = []
                for h in history:
                    timestamps.append(datetime.fromtimestamp(int(h['clock'])))
                    values.append(float(h['value']))
                item.set_timestamps(timestamps)
                item.set_values(values)
        return
    
    def run(self):
        self.collect_items_by_key()
        self.collect_history()