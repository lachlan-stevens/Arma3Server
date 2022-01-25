import os
import re
import subprocess
import ipaddress

import local
import workshop


def mod_param(name, mods):
    return ' -{}="{}" '.format(name, ";".join(mods))


def env_defined(key):
    return key in os.environ and len(os.environ[key]) > 0


CONFIG_FILE = os.environ["ARMA_CONFIG"]
OP_MODE = os.environ["OP_MODE"]
KEYS = "/arma3/keys"
HEADLESS_IP = os.environ["HOST_IP"]

if not os.path.isdir(KEYS):
    if os.path.exists(KEYS):
        os.remove(KEYS)
    os.makedirs(KEYS)

# Install Arma

steamcmd = ["/steamcmd/steamcmd.sh"]
steamcmd.extend(["+force_install_dir", "/arma3"])
steamcmd.extend(["+login", os.environ["STEAM_USER"], os.environ["STEAM_PASSWORD"]])
steamcmd.extend(["+app_update", "233780"])
if env_defined("STEAM_BRANCH"):
    steamcmd.extend(["-beta", os.environ["STEAM_BRANCH"]])
if env_defined("STEAM_BRANCH_PASSWORD"):
    steamcmd.extend(["-betapassword", os.environ["STEAM_BRANCH_PASSWORD"]])
steamcmd.extend(["validate", "+quit"])
subprocess.call(steamcmd)

# Mods

mods = []

if os.environ["MODS_PRESET"] != "":
    mods.extend(workshop.preset(os.environ["MODS_PRESET"]))

if os.environ["MODS_LOCAL"] == "true" and os.path.exists("mods"):
    mods.extend(local.mods("mods"))

launch = "{} -limitFPS={} -world={} {} {}".format(
    os.environ["ARMA_BINARY"],
    os.environ["ARMA_LIMITFPS"],
    os.environ["ARMA_WORLD"],
    os.environ["ARMA_PARAMS"],
    mod_param("mod", mods),
)

if os.environ["ARMA_CDLC"] != "":
    for cdlc in os.environ["ARMA_CDLC"].split(";"):
        launch += " -mod={}".format(cdlc)

print("Starting container in {} mode".format(OP_MODE))

clients = int(os.environ["HEADLESS_CLIENTS"])

if OP_MODE.lower() == "basic":   

    clients = int(os.environ["HEADLESS_CLIENTS"])
    print("Headless Clients:", clients)
    
    if clients != 0:
        with open("/arma3/configs/{}".format(CONFIG_FILE)) as config:
            data = config.read()
            regex = r"(.+?)(?:\s+)?=(?:\s+)?(.+?)(?:$|\/|;)"

            config_values = {}

            matches = re.finditer(regex, data, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                config_values[match.group(1).lower()] = match.group(2)

            if "headlessclients[]" not in config_values:
                data += '\nheadlessclients[] = {"127.0.0.1"};\n'
            if "localclient[]" not in config_values:
                data += '\nlocalclient[] = {"127.0.0.1"};\n'

            with open("/tmp/arma3.cfg", "w") as tmp_config:
                tmp_config.write(data)
            launch += ' -config="/tmp/arma3.cfg" -cfg="/arma3/configs/{}"'.format(BASIC_CONFIG_FILE)

        client_launch = launch
        client_launch += " -client -connect=127.0.0.1"
        if "password" in config_values:
            client_launch += " -password={}".format(config_values["password"])

        for i in range(0, clients):
            hc_launch = client_launch + ' -name="{}-hc-{}"'.format(
                os.environ["ARMA_PROFILE"], i
            )
            print("LAUNCHING ARMA CLIENT {} WITH".format(i), hc_launch)
            subprocess.Popen(hc_launch, shell=True)

    else:
        launch += ' -config="/arma3/configs/{}" -cfg="/arma3/configs/{}"'.format(CONFIG_FILE, BASIC_CONFIG_FILE)

    launch += ' -port={} -name="{}" -profiles="/arma3/configs/profiles"'.format(
    os.environ["PORT"], os.environ["ARMA_PROFILE"]
)

    if os.path.exists("servermods"):
        launch += mod_param("serverMod", local.mods("servermods"))



    print("LAUNCHING ARMA SERVER WITH", launch, flush=True)
    os.system(launch)

elif OP_MODE.lower() == "standalone":
    
    if (clients > 0):
        print("[WARNING]: HEADLESS_CLIENTS set to {}. Expected for standalone mode: 0. Ignoring.".format{clients})

    if HEADLESS_IP != "":
        headless_list = []
        for ip in HEADLESS_IP.split(";"):
            headless_list+= ipaddress.ip_network(ip).hosts()

        with open("/arma3/configs/{}".format(CONFIG_FILE)) as config:
            data = config.read()
        regex = r"(.+?)(?:\s+)?=(?:\s+)?(.+?)(?:$|\/|;)"

        config_values = {}

        matches = re.finditer(regex, data, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            config_values[match.group(1).lower()] = match.group(2)

        config_ip = ""
        for ip in headless_list:
            config_ip += ' {"{ip}"}'.replace('{ip}', str(ip))

        if "headlessclients[]" not in config_values:
            data += '\nheadlessclients[] ={};\n'.format(config_ip)
        if "localclient[]" not in config_values:
            data += '\nlocalclient[] = {};\n'.format(config_ip)

        with open("/tmp/arma3.cfg", "w") as tmp_config:
            tmp_config.write(data)
        launch += ' -config="/tmp/arma3.cfg" -cfg="/arma3/configs/{}"'.format(BASIC_CONFIG_FILE)

    launch += ' -port={} -name="{}" -profiles="/arma3/configs/profiles"'.format(
    os.environ["PORT"], os.environ["ARMA_PROFILE"]
)

    if os.path.exists("servermods"):
        launch += mod_param("serverMod", local.mods("servermods"))



    print("LAUNCHING ARMA SERVER WITH", launch, flush=True)
    os.system(launch)

elif OP_MODE.lower() == "headless":
        
    host_ip = ""
    try: 
        host_ip =IPv4Network(os.environ(HOST_IP))
    except:
        print("[ERROR]: Valid IPv4 Host IP is required for headless mode. Exiting.")
    else:
        with open("/arma3/configs/{}".format(CONFIG_FILE)) as config:
            data = config.read()
            regex = r"(.+?)(?:\s+)?=(?:\s+)?(.+?)(?:$|\/|;)"

            config_values = {}

            matches = re.finditer(regex, data, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                config_values[match.group(1).lower()] = match.group(2)

            if "headlessclients[]" not in config_values:
                data += '\nheadlessclients[] = {"127.0.0.1"};\n'
            if "localclient[]" not in config_values:
                data += '\nlocalclient[] = {"127.0.0.1"};\n'

            with open("/tmp/arma3.cfg", "w") as tmp_config:
                tmp_config.write(data)
            launch += ' -config="/tmp/arma3.cfg" -cfg="/arma3/configs/{}"'.format(BASIC_CONFIG_FILE)

        launch += " -client -connect={}".format(host_ip)
        if "password" in config_values:
            client_launch += " -password={}".format(config_values["password"])


        launch += ' -name="{}-hc-{}"'.format(
                os.environ["ARMA_PROFILE"], os.uname()[1]
            )
        print("LAUNCHING ARMA CLIENT {} WITH".format(i), launch)
        os.system(launch)