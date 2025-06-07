import summoner.connectors as connectors

CONNECTION_FUNCS = {
    "rdp": connectors.rdp_connection,
    "vnc": connectors.vnc_connection,
    "ssh": connectors.ssh_connection,
}
