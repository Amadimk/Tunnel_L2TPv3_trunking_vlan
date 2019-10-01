#!/usr/bin/python
# coding=utf8

# la commande de conversion vers le graph est :
#  dot -Tpng graph.dot -o graph.png

import subprocess


def get_list(c):
	elements = subprocess.check_output(c,shell=True).splitlines()
	return [e.split('#') if ('#' in e) else e for e in elements]

interface_desc = """        "%s" [label=<
            <table border="0" cellborder="1" cellspacing="0" cellpadding="4">
                <tr><td bgcolor="lightblue"><b>%s</b></td></tr>
                <tr><td align="left">IP: %s</td></tr>
            </table>
        >];"""
switch_desc = """        "%s" [label=<
            <table border="0" cellborder="1" cellspacing="0" cellpadding="4">
                <tr><td bgcolor="orange"><b>%s</b></td></tr>
            </table>
        >];"""

nom_fichier = 'build_architecture'
cat_fichier = 'cat '+nom_fichier

list_hosts_command = cat_fichier+"|awk '/ip\s+netns\s+add/ { print $4 }'"
list_switches_command = cat_fichier+"|awk '/ovs-vsctl\s+add-br/ { print $3 }'"
list_veths_command = cat_fichier+"|awk '/ip\s+l(ink)?\s+add/ { print $9 \"#\" $4 }'"
list_ports_command = cat_fichier+"|awk '/ovs-vsctl\s+add-port/ { print $3 \"#\" $4}'"
list_addresses_command = cat_fichier+"|awk '/ip a(ddress)?\s*add\s+dev\s+/ { print $9 \"#\" $10 }'"
titre_graphe_command = cat_fichier+"|sed -n 's/^# graphe : \(.*\)/\\1/p'" 

list_hosts = get_list(list_hosts_command)
list_switches = get_list(list_switches_command)
list_veths = get_list(list_veths_command)
list_ports = get_list(list_ports_command)
list_addresses = get_list(list_addresses_command)
titre_graphe = subprocess.check_output(titre_graphe_command,shell=True).rstrip('\n')

nom_graphe = titre_graphe or "Net Lab" 

#print list_hosts
#print list_switches
#print list_veths
list_veths = [sorted(x,cmp=lambda x,y: -1 if (x[:x.find('-')] in list_switches) else 1)  for x in list_veths]
#print list_veths
#print list_ports
#print list_addresses

print """digraph G { 
    label = "%s";
    labelloc = top;
 
    node [shape=record];
    edge [dir=both];"""%(nom_graphe)

compteur = 0
for h in list_hosts:
	print """subgraph cluster_%d {
		label = %s;
	"""%(compteur,h)
	compteur+=1
	interfaces = [i for i in list_addresses if i[0].startswith(h)]
	for i in interfaces:
		print interface_desc%(i[0],i[0],i[1])
	print """	}"""	

for s in list_switches:
	print """subgraph cluster_%d {
		label = %s;
	"""%(compteur,s)
	compteur+=1
	print switch_desc%(s,s)
	print """	}"""

dico_veths = dict(list_veths)
for p in list_ports:
	print """ "%s"->"%s"; """%(p[0],dico_veths[p[1]])
print "}"
