# Arma 3 Dedicated Server

![Docker Pulls](https://img.shields.io/docker/pulls/lachlancstevens/arma3-server?style=for-the-badge)

This is a docker image for hosting an Arma 3 dedicated server. It is forked from [BrettMayson's image](https://github.com/brettmayson/arma3server), with some changes made by me to fix a couple of issues I was having with it, as well as making modification of the basic.cfg settings a little bit easier.

I use this in Kubernetes with Traefik, however I've included the Docker CLI and docker-compose settings based on BrettMayson's original documentation.

## Usage

### Docker CLI

```s
    docker create \
        --name=arma-server \
        -p 2302:2302/udp \
        -p 2303:2303/udp \
        -p 2304:2304/udp \
        -p 2305:2305/udp \
        -p 2306:2306/udp \
        -v path/to/missions:/arma3/mpmissions \
        -v path/to/configs:/arma3/configs \
        -v path/to/mods:/arma3/mods \
        -v path/to/servermods:/arma3/servermods \
        -e ARMA_CONFIG=main.cfg \
        -e STEAM_USER=myusername \
        -e STEAM_PASSWORD=mypassword \
        -e ARMA_BASIC=basic.cfg \
        lachlancstevens/arma3-server
```

### docker-compose

Use the docker-compose.yml file inside a folder. It will automatically create 4 folders in which the missions, configs, mods and servermods can be loaded.

Copy the `.env.example` file to `.env`, containing at least `STEAM_USER` and `STEAM_PASSWORD`.

Use `docker-compose start` to start the server.

Use `docker-compose logs` to see server logs.

Use `docker-compose down` to shutdown the server.

The `network_mode: host` can be changed to explicit ports if needed.

Use `docker-compose up -d` to start the server, detached.

See [Docker-compose](https://docs.docker.com/compose/install/#install-compose) for an installation guide.

Profiles are saved in `/arma3/configs/profiles`

## Parameters

| Parameter                     | Function                                                  | Default |
| -------------                 |--------------                                             | - |
| `-p 2302-2306`                | Ports required by Arma 3 |
| `-v /arma3/mpmission`         | Folder with MP Missions |
| `-v /arma3/configs`           | Folder containing config files |
| `-v /arma3/mods`              | Mods that will be loaded by clients |
| `-v /arma3/servermods`        | Mods that will only be loaded by the server |
| `-e PORT`                     | Port used by the server, (uses PORT to PORT+3)            | 2302 |
| `-e ARMA_BINARY`              | Arma 3 server binary to use, `./arma3server_x64` for x64   | `./arma3server` |
| `-e ARMA_CONFIG`              | Config file to load from `/arma3/configs`                 | `main.cfg` |
| `-e ARMA_PROFILE`             | Profile name, stored in `/arma3/configs/profiles`         | `main` |
| `-e ARMA_WORLD`               | World to load on startup                                  | `empty` |
| `-e ARMA_LIMITFPS`            | Maximum FPS | `1000` |
| `-e ARMA_CDLC`                | cDLCs to load |
| `-e STEAM_BRANCH`             | Steam branch used by steamcmd | `public` |
| `-e STEAM_BRANCH_PASSWORD`    | Steam branch password used by steamcmd |
| `-e STEAM_USER`               | Steam username used to login to steamcmd |
| `-e STEAM_PASSWORD`           | Steam password |
| `-e HEADLESS_CLIENTS`         | Launch n number of headless clients                       | `0` |
| `-e MODS_LOCAL`               | Should the mods folder be loaded | `true` |
| `-e MODS_PRESET`              | An Arma 3 Launcher preset to load |
| `-e BASIC_CONFIG`             | Basic config file to load from `arma3/configs`            |`basic.cfg` |

The Steam account does not need to own Arma 3, but must have Steam Guard disabled.

List of Steam branches can be found on the Community Wiki, [Arma 3: Steam Branches](https://community.bistudio.com/wiki/Arma_3:_Steam_Branches)

## Creator DLC

To use a Creator DLC the `STEAM_BRANCH` must be set to `creatordlc`

| Name | Flag |
| ---- | ---- |
| [CSLA Iron Curtain](https://store.steampowered.com/app/1294440/Arma_3_Creator_DLC_CSLA_Iron_Curtain/) | CSLA |
| [Global Mobilization - Cold War Germany](https://store.steampowered.com/app/1042220/Arma_3_Creator_DLC_Global_Mobilization__Cold_War_Germany/) | GM |
| [S.O.G. Prairie Fire](https://store.steampowered.com/app/1227700/Arma_3_Creator_DLC_SOG_Prairie_Fire) (see below) | vn |
| [Western Sahara](https://store.steampowered.com/app/1681170/Arma_3_Creator_DLC_Western_Sahara/) | WS |

### Example

`-e ARMA_CDLC="csla;gm;vn;ws"`

### A note on S.O.G. Prairie Fire Headless Clients

There is a bug in the S.O.G. Prairie Fire CDLC which causes headless clients to crash on launch. This appears to be caused by the way the main menu UI is created (the headless client has no screen resolution, which causes divide by zero errors. To get around this on my own servers I use the below Steam Workshop asset (I'm not providing an endorse and do not have any association with the asset or its creators).

[S.O.G. Prairie Fire Vanilla Main Menu](https://steamcommunity.com/sharedfiles/filedetails/?id=2487302280)

## Loading mods

### Local

1. Place the mods inside `/mods` or `/servermods`.
2. Be sure that the mod folder is all lowercase and does not show up with quotation marks around it when listing the directory eg `'@ACE(v2)'`
3. Run the following command from the mods and/or servermods directory to confirm that all the files are lowercase.
    `find . -depth -exec rename 's/(.*)\/([^\/]*)/$1\/\L$2/' {} \;`
    If this is NOT the case, the mods will prevent the server from booting.
4. Make sure that each mod contains a lowercase `/addons` folder. This folder also needs to be lowercase in order for the server to load the required PBO files inside.
5. Start the server.

### Workshop

Set the environment variable `MODS_PRESET` to the HTML preset file exported from the Arma 3 Launcher. The path can be local file or a URL. A volume can be created at `/arma3/steamapps/workshop/content/107410` to preserve the mods between containers.

`-e MODS_PRESET="my_mods.html"`

`-e MODS_PRESET="http://example.com/my_mods.html"`
