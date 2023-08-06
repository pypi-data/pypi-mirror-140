"""
Py-Cord REST ext
~~~~~~~~~~~~~~~~~~~

:copyright: 
:license: MIT, see LICENSE for more details.
"""
import threading
from flask import Flask, jsonify, request, redirect
import discord
from discord.ext.commands import Bot as DefaultBot
import typing as T

class BASEREST:
    allows_ips = []
    def __init__(self, 
                port : int,
                host="0.0.0.0"):
        self.host = host
        self.port = port
        self.APP = Flask("py-cord REST")

    def allow(self, ip : str):
        """
        Allow the IP address to connect to the API.
        """
        if ip not in self.allows_ips:
            self.allows_ips.append(ip)

    def route(self, rule, **kwds):
        """
        Alias for Flask.route method
        """
        return self.APP.route(rule, **kwds)
    
    def _run(self):
        self.APP.run(self.host, self.port, debug=False, threaded=True)
    
    def _start(self):
        """
        Start REST Service
        """
        t = threading.Thread(target=self._run)
        t.start()

class BotREST(BASEREST):
    def __init__(self,                 
                bot: T.Union[discord.Bot, DefaultBot], 
                port : int,
                host="0.0.0.0"):
        
        self._bot = bot
        super().__init__(port, host)
    
    def start(self):
        @self.route("/rest/<page>")
        def basement(page):
            req = request
            if req.remote_addr in self.allows_ips:
                if page == "info":
                    return jsonify(
                        ping=round(self._bot.latency), 
                        guilds=len(self._bot.guilds),
                        members=len(self._bot.users)
                    )
                # TODO : All pages soon
            else:
                return redirect("http://127.0.0.1")
        
        self._start()