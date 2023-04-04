from pyzabbix import ZabbixAPI
from datetime import datetime, timedelta

class Zapi:
    def __init__(self, url, token, ssl=False):
        self.API = ZabbixAPI(url)
        self.API.session.verify = ssl
        self.API.login(api_token=token)
        print("Connected to Zabbix API Version %s" % self.API.api_version())

    # def get_hostid_by_name(self, host_name: str):
    #     host = self.API.host.get(
    #         output="extend", 
    #         search={"name":host_name}
    #     )
    #     if not host:
    #         print(f"Host {host_name}: not found")
    #         return None
    #     return host[0]['hostid']

    # def get_hostids(self, host_names):
    #     hostids = []
    #     for name in host_names:
    #         hostid = self.get_hostid_by_name(name)
    #         if not hostid: continue
    #         hostids.append(hostid)
    #     return hostids

    def get_itemids_and_hostid(self, host_names: list, key = "system.cpu.util"):
        hosts = []
        for name in host_names:
            data = self.API.item.get(
                output="extend",
                search={"key_": key},
                host=name,
            )
            if not data:
                print(f"No data for {name}")
                continue
            itemids = []

            for item in data:
                itemids.append(item["itemid"])
            hosts.append({"_id": data[0]["hostid"], "itemids": itemids})
        return hosts
    
    def get_history_by_itemid(self, hostid, itemid):
        data = self.API.history.get(
            output="extend", 
            hostids=hostid, 
            history=0, 
            sortorder='ASC', 
            sortfield="clock", 
            itemids=itemid, 
            time_from=int((datetime.now() - timedelta(days=1)).timestamp()),
        )

        if not data:
            print(f"Error for {hostid}")
            return
        
        timestamps = []
        values = []
        for item in data:
            timestamps.append(datetime.fromtimestamp(int(item['clock'])))
            values.append(float(item['value']))
        return timestamps, values
        
    def get_history_all_host(self, hosts):
        payload = []
        for host in hosts:
            dataitems = []
            for itemid in host["itemids"]:
                timestamps, values = self.get_history_by_itemid(host['_id'], itemid)
                dataitems.append((timestamps, values))
            payload.append({"_id": host['_id'], "dataitems": dataitems})
        return payload
    
