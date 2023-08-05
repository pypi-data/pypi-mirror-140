import sys 
import os
import time

import aiohttp
from sqlalchemy.sql import select, delete
import kaeru.database
from kaeru.tables import AnswerTable, UserTable

sys.path.append(os.environ['HOME'] + "/.config/kaeru/")
from config import gisei, master, wts_target

from alright import WhatsApp


engine = kaeru.database.engine
mc = {0: "A", 1:"B", 2:"C", 3: "D"}


async def get_assignment(date):
    async with aiohttp.ClientSession() as s:
        await s.post(
            "https://fireflies.chiculture.org.hk/api/core/auth",
            data=gisei | {"web": 1, "persist": True},
        )
        async with s.get(
            f"https://fireflies.chiculture.org.hk/api/quiz/assignments/{date}"
        ) as resp:
            json_data = await resp.json()
    question_list = json_data["article"]["questions"]
    answer_data = {}
    answer_data["assignment"] = json_data["id"]
    answer_data["answers"] = []
    answer_data["answers_short"] = ""
    for q in question_list:
        try:
            answer_data["answers"].append(
                {"question": q["_id"], "answered": q["answer"]}
            )
            answer_data["answers_short"] += mc[q["answer"]]
        except:
            answer_data["answers"].append({"question": q["_id"], "answered": 2})
    return answer_data


async def submit_answers(email, password, answer_data):
    async with aiohttp.ClientSession() as s:
        await s.post(
            "https://fireflies.chiculture.org.hk/api/core/auth",
            data={"email": email, "password": password, "web": 1, "persist": True},
        )
        await s.post(
            "https://fireflies.chiculture.org.hk/api/quiz/answers", json=answer_data
        )
        async with s.post(
            "https://fireflies.chiculture.org.hk/api/quiz/answers/extra-read",
            json={"assignment": answer_data["assignment"]},
        ) as resp:
            print(email, await resp.text())
            return await resp.json()


async def get_answers(date):
    async with engine.begin() as conn:
        answer_list = await conn.execute(
            select(AnswerTable).where(
                AnswerTable.c.date == date
            )
        )
    answer_data = answer_list.first()
    if answer_data:
        print(answer_data._asdict())
        return answer_data._asdict()
    await submit_answers(**gisei, answer_data=await get_assignment(date))
    answer_data = await get_assignment(date)
    async with aiohttp.ClientSession() as s:
        await s.post(
            "https://fireflies.chiculture.org.hk/api/core/auth",
            data=master | {"web": 1, "persist": True},
        )
        async with s.get(
            f"https://fireflies.chiculture.org.hk/api/quiz/assignments/{date}"
        ) as resp:
            json_data = await resp.json()
    answer_data["assignment"] = json_data["id"]
    answer_data["date"] = date
    async with engine.begin() as conn:
        await conn.execute(AnswerTable.insert(), answer_data)
    return answer_data


async def add_user(email, password):
    async with engine.begin() as conn:
        await conn.execute(UserTable.insert(), {"email": email, "password": password})


async def get_users():
    async with engine.begin() as conn:
        users = await conn.execute(select(UserTable))
    return users


async def delete_answer(date):
    async with engine.begin() as conn:
        await conn.execute(delete(AnswerTable).where(AnswerTable.c.date == date))


async def delete_user(email):
    async with engine.begin() as conn:
        await conn.execute(delete(UserTable).where(UserTable.c.email == email))

def notify_whatsapp(answer_data):
    messenger = WhatsApp()
    if not wts_target:
        return print("Please set a target group / user!")
    messenger.find_by_username(wts_target)
    message = answer_data["date"] + ": " + answer_data["answers_short"]
    messenger.send_message(message)
    time.sleep(5)
