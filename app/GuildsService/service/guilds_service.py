from pymongo import MongoClient
from bson.objectid import ObjectId
from models.guild import Guild, Member, GuildCreation
from fastapi import HTTPException
from typing import Union


class GuildsService:
    def __init__(self):
        self.client = MongoClient("mongodb", 27017)
        db = self.client["guilds"]
        self.guilds = db['guilds']
        self.members = db['members']

    async def get_guilds(self):
        guilds = list(self.guilds.find())
        return {"guilds": guilds}

    async def get_members(self, gid: str):
        members = list(self.members.find({"gid": gid}))
        return members

    async def create_guild(self, guild: GuildCreation):
        result = self.guilds.insert_one(Guild(**guild.dict()).dict())
        if result.acknowledged:
            return str(result.inserted_id)
        else:
            return False

    async def join_guild(self, member: Member):
        # member_exists = self.members.find_one(member.dict())
        # if member_exists:
        #     return False

        # guild = self.guilds.find_one({"_id": ObjectId(member.gid)})
        # if not guild:
        #     return False

        self.members.insert_one(member.dict())
        self.guilds.update_one({"_id": ObjectId(member.gid)}, {"$inc": {"num_members": 1}})
        return True

    async def leave_guild(self, member: Member):
        self.guilds.update_one({"_id": ObjectId(member.gid)}, {"$inc": {"num_members": -1}})
        self.members.delete_one(member.dict())
        guild = self.guilds.find_one({"_id": ObjectId(member.gid)})
        # if not guild:
        #     return False
        if guild["num_members"] == 0:
            await self.delete_guild(member.gid)
        return True

    async def delete_guild(self, gid: str):
        self.guilds.delete_one({"_id": ObjectId(gid)})
        self.members.delete_many({"gid": gid})
        return True
