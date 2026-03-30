## Description

*Monitoring tools are cruical part of IT, where we can check and see and also debug what is happening based on realtime information of devices and services*

*Below are lists of monitoring tools that being used both internally and externally*

[Terrabit](https://www.terrabitnet.com/) - Monitoring tools for internet provided by ISP for our company
 - Proprietary: https://mrtg.terabit.net.id/

[Beszel](https://github.com/henrygd/beszel) - Device monitoring tools for computer, laptop and VMs
- Hosted internally on netmon VMs: http://10.10.10.7:8090/
- *Has notification linked to IT WhatsApp group*

[Uptime Kuma](https://github.com/louislam/uptime-kuma) - API monitoring tools for internal and external services
- Hosted on external VPS: http://103.94.239.66:3001
- *Has notification linked to IT WhatsApp group*

[Zabbix](https://www.zabbix.com/) - Internet monitoring tools for bandwith and uplink
 - Hosted internally on netmon VMs: http://10.10.10.7/zabbix/

The credentials for these service can be found on Tech Development WhatsApp group description

Some of these monitoring tools have webhooks to notify the group if something went wrong, you can disable and enable as you see fit