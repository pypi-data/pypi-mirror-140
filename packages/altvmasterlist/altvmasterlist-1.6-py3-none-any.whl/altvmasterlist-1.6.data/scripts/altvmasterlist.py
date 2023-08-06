#!/usr/bin/env python3
from urllib3 import PoolManager
from config import config
from json import loads

pool = PoolManager()

class Server:
    def __init__(self, active, id, maxPlayers, players, name, locked, host, port, gameMode, website, language, description, verified, promoted, useEarlyAuth, earlyAuthUrl, useCdn, cdnUrl, useVoiceChat, tags, bannerUrl, branch, build, version, lastUpdate):
        self.active = active
        self.id = id
        self.maxPlayers = maxPlayers
        self.players = players
        self.name = name
        self.locked = locked
        self.host = host
        self.port = port
        self.gameMode = gameMode
        self.website = website
        self.language = language
        self.description = description
        self.verified = verified
        self.promoted = promoted
        self.useEarlyAuth = useEarlyAuth
        self.earlyAuthUrl = earlyAuthUrl
        self.useCdn = useCdn
        self.cdnUrl = cdnUrl
        self.useVoiceChat = useVoiceChat
        self.tags = tags
        self.bannerUrl = bannerUrl
        self.branch = branch
        self.build = build
        self.version = version
        self.lastUpdate = lastUpdate

    def get_json(self):
        return {
            "active": self.active,
            "id": self.id,
            "maxPlayers": self.maxPlayers,
            "players": self.players,
            "name": self.name,
            "locked": self.locked,
            "host": self.host,
            "port": self.port,
            "gameMode": self.gameMode,
            "website": self.website,
            "language": self.language,
            "description": self.description,
            "verified": self.verified,
            "promoted": self.promoted,
            "useEarlyAuth": self.useEarlyAuth,
            "earlyAuthUrl": self.earlyAuthUrl,
            "useCdn": self.useCdn,
            "cdnUrl": self.cdnUrl,
            "useVoiceChat": self.useVoiceChat,
            "tags": self.tags,
            "bannerUrl": self.bannerUrl,
            "branch": self.branch,
            "build": self.build,
            "version": self.version,
            "lastUpdate": self.lastUpdate
        }

def request(url):
    request = pool.request('GET', url, preload_content=False)
    apijson = loads(request.data)
    request.release_conn()
    return apijson

def get_server_stats():
    return request(config.all_server_stats_link)

def get_servers():
    return_servers = []
    servers = request(config.all_servers_link)
    for server in servers:
        temp_server = Server("unknown", server["id"], server["maxPlayers"], server["players"], server["name"], server["locked"], server["host"], server["port"], server["gameMode"], server["website"], server["language"], server["description"], server["verified"], server["promoted"], server["useEarlyAuth"], server["earlyAuthUrl"], server["useCdn"], server["cdnUrl"], server["useVoiceChat"], server["tags"], server["bannerUrl"], server["branch"], server["build"], server["version"], server["lastUpdate"])
        return_servers.append(temp_server)
        
    return return_servers

def get_server_by_id(id):
    temp_data = request(config.server_link.format(id))
    return_server = Server(temp_data["active"], temp_data["info"]["id"], temp_data["info"]["maxPlayers"], temp_data["info"]["players"], temp_data["info"]["name"], temp_data["info"]["locked"], temp_data["info"]["host"], temp_data["info"]["port"], temp_data["info"]["gameMode"], temp_data["info"]["website"], temp_data["info"]["language"], temp_data["info"]["description"], temp_data["info"]["verified"], temp_data["info"]["promoted"], temp_data["info"]["useEarlyAuth"], temp_data["info"]["earlyAuthUrl"], temp_data["info"]["useCdn"], temp_data["info"]["cdnUrl"], temp_data["info"]["useVoiceChat"], temp_data["info"]["tags"], temp_data["info"]["bannerUrl"], temp_data["info"]["branch"], temp_data["info"]["build"], temp_data["info"]["version"], temp_data["info"]["lastUpdate"])
    return return_server

def get_server_by_id_avg(id, time):
    return request(config.server_average_link.format(id, time))

def get_server_by_id_avg(id, time):
    return request(config.server_max_link.format(id, time))

if __name__ == "__main__":
    exit()