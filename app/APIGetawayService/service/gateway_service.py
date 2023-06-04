from common.game_data.stats import Stats
from common.game_data.resources import Resources
from common.game_data.user import User
from kafka import KafkaProducer

import requests
import consul
import json
import random

KAFKA_SERVER = 'kafka-server:9092'
GAME_DATA_TOPIC = 'game-data'
GAME_STATS_TOPIC = 'game-stats'

REGISTER_SERVICE_URL = 'http://register-service:8080/user/'
LOGIN_SERVICE_URL = 'http://login-service:8080/login/user/'
VALIDATION_SERVICE_URL = 'http://validation-service:8080/c/'

STATS_GAME_DATA_URL = 'http://game_data:8000/stats?player_id='
RESOURCES_GAME_DATA_URL = 'http://game_data:8000/resources?player_id='
AVERAGE_GAME_DATA_URL = 'http://game_data:8000/resources?player_id='


class GatewayService:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER])
        self.consul_service = consul.Consul(host="consul")

    # Returns a boolean whether the validation was successful
    def verify_request(self, uid: str, token: str):
        url, port = self.get_address("validation")
        response = requests.post(
            url=f"http://{url}:{port}/validate", json={"uid": uid, "token": token})

        if response.text == "true":
            return True

        return False

    def get_address(self, service_name):
        consul_info = self.consul_service.health.service(service_name)[1]
        address = random.choice(consul_info)["Service"]["Address"]
        port = random.choice(consul_info)["Service"]["Port"]
        return address, port

    def handle_register_operation(self, user_data: User):
        response = requests.post(
            url=REGISTER_SERVICE_URL, json={"username": user_data.username, "password": user_data.password})

        return response.text

    def handle_login_operation(self, user_data: User):
        response = requests.post(
            url=LOGIN_SERVICE_URL, json=dict(user_data))

        return response.text

    def get_game_resources(self, player_id: int):
        url, port = self.get_address("game-data")
        response = requests.get(url=f'http://{url}:{port}/resources?player_id=' + str(player_id))

        return response.json()

    def set_game_resources(self, player_id: int, resources: Resources):
        # Verify the sender
        if (not self.verify_request(resources.player_id, resources.token)):
            print("Bad token: " + resources.token, flush=True)
            return {"success": False}

        resources.token = None

        # sync for now
        metadata = self.producer.send(GAME_DATA_TOPIC, json.dumps(
            resources.dict()).encode()).get(timeout=10)

        return {"success": True, "topic": metadata.topic}

    def get_game_stats(self, player_id: int):
        url, port = self.get_address("game-data")
        response = requests.get(url=f"http://{url}:{port}/stats?player_id=" + str(player_id))

        return response.json()

    def set_game_stats(self, player_id: int, stats: Stats):
        # Verify the sender
        if (not self.verify_request(stats.player_id, stats.token)):
            print("Bad token: " + stats.token, flush=True)
            return {"success": False}

        stats.token = None

        # set gata in game_data
        metadata = self.producer.send(GAME_STATS_TOPIC, json.dumps(
            stats.dict()).encode()).get(timeout=10)

        return {"success": True, "topic": metadata.topic}

    def get_game_leagueboard(self, limit):
        return {"limit": limit}

    def get_game_data_average(self, player_id: int):
        url, port = self.get_address("game-data")
        response = requests.get(url=f'http://{url}:{port}/resources?player_id=' + str(player_id))

        return response.json()
