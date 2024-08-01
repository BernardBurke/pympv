from jellyfin_apiclient_python import JellyfinClient

client = JellyfinClient()

client.config.data["app.name"] = 'pyfin'
client.config.data["app.version"] = '0.0.1'
client.authenticate({"Servers": [{"AccessToken": "ef62460ed3d84110be1f36fa895b58d9", "address": "synth2" }]}, discover=False)
