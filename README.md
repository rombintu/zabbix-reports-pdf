## Zabbix PDF Reports (BETA)

### Install
```bash
git clone <this repo>; cd <this repo>
poetry install
poetry shell # Create .venv
source .venv/bin/activate
python3 main.py --help
python3 --url https://zabbix.com:8080 --token <YOUR TOKEN> --hostfile ./hostfile.txt
```

### Hostfile example
```
Zabbix server
Zabbix-agent0
some-host-from-zabbix
```