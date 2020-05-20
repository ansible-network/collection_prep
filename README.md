# 1.0.0 prep engine


## CONTENT UPDATER
```console
python update.py -c arista.eos -p ./
```

```console
INFO      -------------------Processing ./arista.eos/plugins/modules/eos_lacp.py
INFO      Updated metadata in ./arista.eos/plugins/modules/eos_lacp.py
INFO      Updated documentation in ./arista.eos/plugins/modules/eos_lacp.py
INFO      Found a resource module
INFO      Setting short desciption to 'LACP resource module'
INFO      Updated examples in ./arista.eos/plugins/modules/eos_lacp.py
INFO      Wrote ./arista.eos/plugins/modules/eos_lacp.py
INFO      Running black against ./arista.eos/plugins/modules/eos_lacp.py
INFO      -------------------Processing ./arista.eos/plugins/modules/eos_static_routes.py
INFO      Updated metadata in ./arista.eos/plugins/modules/eos_static_routes.py
INFO      Updated documentation in ./arista.eos/plugins/modules/eos_static_routes.py
INFO      Found a resource module
INFO      Setting short desciption to 'Static routes resource module'
INFO      Updated examples in ./arista.eos/plugins/modules/eos_static_routes.py
INFO      Wrote ./arista.eos/plugins/modules/eos_static_routes.py
INFO      Running black against ./arista.eos/plugins/modules/eos_static_routes.py
INFO      -------------------Processing ./arista.eos/plugins/action/__init__.py
WARNING   Failed to find DOCUMENTATION assignment
WARNING   Skipped ./arista.eos/plugins/action/__init__.py: No module name found
```

## DOC GENERATOR

This is intended to operate against the repository clone.

This will generate an RST file for each plugin in the collection docs folder and add a table of links for all plugin types in the REAMDE.md

Ensure the collection README.md has the following in it:
```

<!--start collection content-->
<!--end collection content-->
```

```console
python add_docs.py -p ./ansible.netcommon     
```

```console
INFO      Setting collection name to ansible.netcommon
INFO      Setting github repository url to https://github.com/ansible-collections/ansible.netcommon
INFO      Linking collection to user collection directory
INFO      This is required for the Ansible fragment loader to find doc fragments
INFO      Attempting to remove existing /home/bthornto/.ansible/collections/ansible_collections/ansible/netcommon
INFO      Deleteing: /home/bthornto/.ansible/collections/ansible_collections/ansible/netcommon
INFO      Creating namepsace directory /home/bthornto/.ansible/collections/ansible_collections/ansible
INFO      Linking collection /home/bthornto/github/collection_update/ansible.netcommon -> /home/bthornto/.ansible/collections/ansible_collections/ansible/netcommon
INFO      Purging content from directory /home/bthornto/github/collection_update/ansible.netcommon/docs
INFO      Making docs directory /home/bthornto/github/collection_update/ansible.netcommon/docs
INFO      Process content in /home/bthornto/github/collection_update/ansible.netcommon/plugins/become
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/become/enable.py
INFO      Process content in /home/bthornto/github/collection_update/ansible.netcommon/plugins/connection
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/connection/httpapi.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/connection/network_cli.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/connection/netconf.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/connection/napalm.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/connection/persistent.py
INFO      Process content in /home/bthornto/github/collection_update/ansible.netcommon/plugins/filter
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/filter/ipaddr.py
INFO      Adding filter plugins cidr_merge,ipaddr,ipmath,ipwrap,ip4_hex,ipv4,ipv6,ipsubnet,next_nth_usable,network_in_network,network_in_usable,reduce_on_network,nthhost,previous_nth_usable,slaac,hwaddr,macaddr
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/filter/network.py
INFO      Adding filter plugins parse_cli,parse_cli_textfsm,parse_xml,type5_pw,hash_salt,comp_type5,vlan_parser
INFO      Process content in /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_l3_interface.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/restconf_get.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_l2_interface.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_static_route.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_linkagg.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_logging.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/telnet.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_system.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/cli_config.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_ping.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_banner.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_lldp.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_interface.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/restconf_config.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/netconf_config.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_vrf.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_lldp_interface.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/netconf_get.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/netconf_rpc.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_get.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_vlan.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_put.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/cli_command.py
INFO      Processing /home/bthornto/github/collection_update/ansible.netcommon/plugins/modules/net_user.py
INFO      Processing 'become' for README
INFO      Processing 'connection' for README
INFO      Processing 'filter' for README
INFO      Processing 'modules' for README
INFO      README.md updated
(venv) ➜  collection_update git:(master) ✗ 
```
