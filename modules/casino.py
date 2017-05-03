import discord
from discord.ext import commands
from utils.dataIO import dataIO
from collections import namedtuple, defaultdict, deque
from datetime import datetime
from copy import deepcopy
from utils import checks
from utils.chat_formatting import pagify, box
from enum import Enum
import os
import time
import logging
import random

default_settings = {"PAYOUT_TIME": 300, "PAYOUT_FLOWERS": 120,
                    "REGISTER_FLOWERS": 0}


class EconomyError(Exception):
    pass


class OnCooldown(EconomyError):
    pass


class InvalidBid(EconomyError):
    pass


class BankError(Exception):
    pass


class AccountAlreadyExists(BankError):
    pass


class NoAccount(BankError):
    pass


class InsufficientBalance(BankError):
    pass


class NegativeValue(BankError):
    pass


class SameSenderAndReceiver(BankError):
    pass


NUM_ENC = "\N{COMBINING ENCLOSING KEYCAP}"

class Bank:

    def __init__(self, bot, file_path):
        self.accounts = dataIO.load_json(file_path)
        self.bot = bot

    def create_account(self, user, *, initial_balance=0):
        server = user.server
        if not self.account_exists(user):
            if server.id not in self.accounts:
                self.accounts[server.id] = {}
            if user.id in self.accounts:  # Legacy account
                balance = self.accounts[user.id]["balance"]
            else:
                balance = initial_balance
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            account = {"name": user.name,
                       "balance": balance,
                       "created_at": timestamp
                       }
            self.accounts[server.id][user.id] = account
            self._save_bank()
            return self.get_account(user)
        else:
            raise AccountAlreadyExists()

    def account_exists(self, user):
        try:
            self._get_account(user)
        except NoAccount:
            return False
        return True

    def withdraw_credits(self, user, amount):
        server = user.server

        if amount < 0:
            raise NegativeValue()

        account = self._get_account(user)
        if account["balance"] >= amount:
            account["balance"] -= amount
            self.accounts[server.id][user.id] = account
            self._save_bank()
        else:
            raise InsufficientBalance()

    def deposit_credits(self, user, amount):
        server = user.server
        if amount < 0:
            raise NegativeValue()
        account = self._get_account(user)
        account["balance"] += amount
        self.accounts[server.id][user.id] = account
        self._save_bank()

    def set_credits(self, user, amount):
        server = user.server
        if amount < 0:
            raise NegativeValue()
        account = self._get_account(user)
        account["balance"] = amount
        self.accounts[server.id][user.id] = account
        self._save_bank()

    def transfer_credits(self, sender, receiver, amount):
        if amount < 0:
            raise NegativeValue()
        if sender is receiver:
            raise SameSenderAndReceiver()
        if self.account_exists(sender) and self.account_exists(receiver):
            sender_acc = self._get_account(sender)
            if sender_acc["balance"] < amount:
                raise InsufficientBalance()
            self.withdraw_credits(sender, amount)
            self.deposit_credits(receiver, amount)
        else:
            raise NoAccount()

    def can_spend(self, user, amount):
        account = self._get_account(user)
        if account["balance"] >= amount:
            return True
        else:
            return False

    def wipe_bank(self, server):
        self.accounts[server.id] = {}
        self._save_bank()

    def get_server_accounts(self, server):
        if server.id in self.accounts:
            raw_server_accounts = deepcopy(self.accounts[server.id])
            accounts = []
            for k, v in raw_server_accounts.items():
                v["id"] = k
                v["server"] = server
                acc = self._create_account_obj(v)
                accounts.append(acc)
            return accounts
        else:
            return []

    def get_all_accounts(self):
        accounts = []
        for server_id, v in self.accounts.items():
            server = self.bot.get_server(server_id)
            if server is None:
                # Servers that have since been left will be ignored
                # Same for users_id from the old bank format
                continue
            raw_server_accounts = deepcopy(self.accounts[server.id])
            for k, v in raw_server_accounts.items():
                v["id"] = k
                v["server"] = server
                acc = self._create_account_obj(v)
                accounts.append(acc)
        return accounts

    def get_balance(self, user):
        account = self._get_account(user)
        return account["balance"]

    def get_account(self, user):
        acc = self._get_account(user)
        acc["id"] = user.id
        acc["server"] = user.server
        return self._create_account_obj(acc)

    def _create_account_obj(self, account):
        account["member"] = account["server"].get_member(account["id"])
        account["created_at"] = datetime.strptime(account["created_at"],
                                                  "%Y-%m-%d %H:%M:%S")
        Account = namedtuple("Account", "id name balance "
                             "created_at server member")
        return Account(**account)

    def _save_bank(self):
        dataIO.save_json("data/casino/bank.json", self.accounts)

    def _get_account(self, user):
        server = user.server
        try:
            return deepcopy(self.accounts[server.id][user.id])
        except KeyError:
            raise NoAccount()


class SetParser:
    def __init__(self, argument):
        allowed = ("+", "-")
        if argument and argument[0] in allowed:
            try:
                self.sum = int(argument)
            except:
                raise
            if self.sum < 0:
                self.operation = "withdraw"
            elif self.sum > 0:
                self.operation = "deposit"
            else:
                raise
            self.sum = abs(self.sum)
        elif argument.isdigit():
            self.sum = int(argument)
            self.operation = "set"
        else:
            raise


class Casino:
    """Economy
    Get rich and have fun with imaginary currency!"""

    def __init__(self, bot):
        global default_settings
        self.bot = bot
        self.bank = Bank(bot, "data/casino/bank.json")
        self.file_path = "data/casino/settings.json"
        self.settings = dataIO.load_json(self.file_path)
        if "PAYOUT_TIME" in self.settings:  # old format
            default_settings = self.settings
            self.settings = {}
        self.settings = defaultdict(lambda: default_settings, self.settings)
        self.payday_register = defaultdict(dict)
        self.slot_register = defaultdict(dict)

    @commands.group(name="casino", pass_context=True)
    async def _casino(self, ctx):
        """Bank operations"""
        if ctx.invoked_subcommand is None:
            await self.bot.say(embed=discord.Embed(description="""b!casino

Casino Group Commands

Commands:
  acctransfer      Transfers account info from old casino. Limit 1 transfer p...
  balance          Shows your number of chips
  exchange         Exchange chips for credits and credits for chips
  info             Shows information about the server casino
  join             Grants you membership access to the casino
  leaderboard      Displays Casino Leaderboard
  memberships      Shows all memberships on the server.
  payday           Gives you some chips
  stats            Shows your casino play stats
  transfer         Transfers chips to another player

Type b!casino command for more info on a command.
You can also type b!casino category for more info on a category."""))

    @_casino.command(pass_context=True, no_pm=True)
    async def register(self, ctx):
        """Registers an account at the Twentysix bank"""
        settings = self.settings[ctx.message.server.id]
        author = ctx.message.author
        credits = 0
        if ctx.message.server.id in self.settings:
            credits = settings.get("REGISTER_CREDITS", 0)
        try:
            account = self.bank.create_account(author, initial_balance=credits)
            await self.bot.say("{} Account opened. Current balance: {}:cherry_blossom:"
                               "".format(author.mention, account.balance))
        except AccountAlreadyExists:
            await self.bot.say("{} You already have an account at the"
                               " Twentysix bank.".format(author.mention))

    @_casino.command(pass_context=True)
    async def balance(self, ctx, user: discord.Member=None):
        """Shows balance of user.
        Defaults to yours."""
        if not user:
            user = ctx.message.author
            try:
                await self.bot.say("{} Your balance is: {}:cherry_blossom:".format(
                    user.mention, self.bank.get_balance(user)))
            except NoAccount:
                await self.bot.say("{} You don't have an account at the"
                                   " Twentysix bank. Type `{}bank register`"
                                   " to open one.".format(user.mention,
                                                          ctx.prefix))
        else:
            try:
                await self.bot.say("{}'s balance is {}".format(
                    user.name, self.bank.get_balance(user)))
            except NoAccount:
                await self.bot.say("That user has no bank account.")

    @_casino.command(pass_context=True)
    async def transfer(self, ctx, user: discord.Member, sum: int):
        """Transfer flowers to other users"""
        author = ctx.message.author
        try:
            self.bank.transfer_credits(author, user, sum)
            logger.info("{}({}) transferred {} :cherry_blossom: to {}({})".format(
                author.name, author.id, sum, user.name, user.id))
            await self.bot.say("{} :cherry_blossom: have been transferred to {}'s"
                               " account.".format(sum, user.name))
        except NegativeValue:
            await self.bot.say("You need to transfer at least 1 :cherry_blossom:.")
        except SameSenderAndReceiver:
            await self.bot.say("You can't transfer :cherry_blossom: to yourself.")
        except InsufficientBalance:
            await self.bot.say("You don't have that many :cherry_blossom: in your bank account.")
        except NoAccount:
            await self.bot.say("That user has no bank account.")

    @_casino.command(name="set", pass_context=True)
    @checks.botcom()
    async def _set(self, ctx, user: discord.Member, credits: SetParser):
        """Sets flowers of user's bank account. See help for more operations
        Passing positive and negative values will add/remove flowers instead
        Examples:
            casino set @Red 26 - Sets 26 flowers
            casino set @Red +2 - Adds 2 flowers
            casino set @Red -6 - Removes 6 flowers"""
        author = ctx.message.author
        try:
            if credits.operation == "deposit":
                self.bank.deposit_credits(user, credits.sum)
                logger.info("{}({}) added {} credits to {} ({})".format(
                    author.name, author.id, credits.sum, user.name, user.id))
                await self.bot.say("{} :cherry_blossom: have been added to {}"
                                   "".format(credits.sum, user.name))
            elif credits.operation == "withdraw":
                self.bank.withdraw_credits(user, credits.sum)
                logger.info("{}({}) removed {} credits to {} ({})".format(
                    author.name, author.id, credits.sum, user.name, user.id))
                await self.bot.say("{} :cherry_blossom: have been withdrawn from {}"
                                   "".format(credits.sum, user.name))
            elif credits.operation == "set":
                self.bank.set_credits(user, credits.sum)
                logger.info("{}({}) set {} :cherry_blossom: to {} ({})"
                            "".format(author.name, author.id, credits.sum,
                                      user.name, user.id))
                await self.bot.say("{}'s :cherry_blossom: have been set to {}".format(
                    user.name, credits.sum))
        except InsufficientBalance:
            await self.bot.say("User doesn't have enough :cherry_blossom:.")
        except NoAccount:
            await self.bot.say("User has no bank account.")

    @_casino.command(pass_context=True, no_pm=True)
    @checks.botcom()
    async def reset(self, ctx, confirmation: bool=False):
        """Deletes all server's bank accounts"""
        if confirmation is False:
            await self.bot.say("This will delete all bank accounts on "
                               "this server.\nIf you're sure, type "
                               "{}bank reset yes".format(ctx.prefix))
        else:
            self.bank.wipe_bank(ctx.message.server)
            await self.bot.say("All bank accounts of this server have been "
                               "deleted.")

    @_casino.command(pass_context=True, no_pm=True)
    async def payout(self, ctx):  # TODO
        """Get some free flowers"""
        author = ctx.message.author
        server = author.server
        id = author.id
        if self.bank.account_exists(author):
            if id in self.payday_register[server.id]:
                seconds = abs(self.payday_register[server.id][
                              id] - int(time.perf_counter()))
                if seconds >= self.settings[server.id]["PAYOUT_TIME"]:
                    self.bank.deposit_credits(author, self.settings[
                                              server.id]["PAYOUT_FLOWERS"])
                    self.payday_register[server.id][
                        id] = int(time.perf_counter())
                    await self.bot.say(
                        "{} :cherry_blossom: +{} :cherry_blossom: :cherry_blossom: :regional_indicator_p: :a: :regional_indicator_y: :o2: "
                        ":regional_indicator_u: :regional_indicator_t: :cherry_blossom: :cherry_blossom: +{} "
                        ":cherry_blossom:".format(
                            author.mention,
                            str(self.settings[server.id]["PAYOUT_FLOWERS"]),
                            str(self.settings[server.id]["PAYOUT_FLOWERS"])))
                else:
                    dtime = self.display_time(
                        self.settings[server.id]["PAYOUT_TIME"] - seconds)
                    await self.bot.say(
                        "{} Too soon. For your next payout you have to"
                        " wait {}.".format(author.mention, dtime))
            else:
                self.payday_register[server.id][id] = int(time.perf_counter())
                self.bank.deposit_credits(author, self.settings[
                                          server.id]["PAYOUT_FLOWERS"])
                await self.bot.say(
                    "{} :cherry_blossom: +{} :cherry_blossom: :cherry_blossom: :regional_indicator_p: :a: :regional_indicator_y: :o2: "
                    ":regional_indicator_u: :regional_indicator_t: :cherry_blossom: :cherry_blossom: +{} "
                    ":cherry_blossom:".format(
                        author.mention,
                        str(self.settings[server.id]["PAYOUT_FLOWERS"]),
                        str(self.settings[server.id]["PAYOUT_FLOWERS"])))
        else:
            await self.bot.say("{} You need an account to receive :cherry_blossom:."
                               " Type `{}bank register` to open one.".format(
                                   author.mention, ctx.prefix))

    @_casino.command(pass_context=True)
    async def ranking(self, ctx, top: int=10):
        """Prints out the server's leaderboard
        Defaults to top 10"""
        # Originally coded by Airenkun - edited by irdumb
        server = ctx.message.server
        if top < 1:
            top = 10
        bank_sorted = sorted(self.bank.get_server_accounts(server),
                             key=lambda x: x.balance, reverse=True)
        if len(bank_sorted) < top:
            top = len(bank_sorted)
        topten = bank_sorted[:top]
        highscore = ""
        place = 1
        for acc in topten:
            highscore += str(place).ljust(len(str(top)) + 1)
            highscore += (acc.name + " ").ljust(23 - len(str(acc.balance)))
            highscore += str(acc.balance) + "\n"
            place += 1
        if highscore != "":
            for page in pagify(highscore, shorten_by=12):
                await self.bot.say(box(page, lang="py"))
        else:
            await self.bot.say("There are no accounts in the bank.")

  
    def already_in_list(self, accounts, user):
        for acc in accounts:
            if user.id == acc.id:
                return True
        return False


    @commands.group(pass_context=True, no_pm=True)
    @checks.botcom()
    async def gamblingset(self, ctx):
        """Changes casino module settings"""
        server = ctx.message.server
        settings = self.settings[server.id]
        if ctx.invoked_subcommand is None:
            msg = "```"
            for k, v in settings.items():
                msg += "{}: {}\n".format(k, v)
            msg += "```"
            await send_cmd_help(ctx)
            await self.bot.say(msg)

    @gamblingset.command(pass_context=True)
    async def payouttime(self, ctx, seconds: int):
        """Seconds between each payout"""
        server = ctx.message.server
        self.settings[server.id]["PAYOUT_TIME"] = seconds
        await self.bot.say("Value modified. At least {} seconds must pass "
                           "between each payout.".format(seconds))
        dataIO.save_json(self.file_path, self.settings)

    @gamblingset.command(pass_context=True)
    async def payoutflowers(self, ctx, credits: int):
        """Flowers earned each payout"""
        server = ctx.message.server
        self.settings[server.id]["PAYOUT_FLOWERS"] = credits
        await self.bot.say("Every payout will now give {} :cherry_blossom:"
                           "".format(credits))
        dataIO.save_json(self.file_path, self.settings)

    @gamblingset.command(pass_context=True)
    async def registerflowers(self, ctx, credits: int):
        """Flowers given on registering an account"""
        server = ctx.message.server
        if credits < 0:
            credits = 0
        self.settings[server.id]["REGISTER_FLOWERS"] = credits
        await self.bot.say("Registering an account will now give {} :cherry_blossom:."
                           "".format(credits))
        dataIO.save_json(self.file_path, self.settings)

    # What would I ever do without stackoverflow?
    def display_time(self, seconds, granularity=2):
        intervals = (  # Source: http://stackoverflow.com/a/24542445
            ('weeks', 604800),  # 60 * 60 * 24 * 7
            ('days', 86400),    # 60 * 60 * 24
            ('hours', 3600),    # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
        )

        result = []

        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(value, name))
        return ', '.join(result[:granularity])


def check_folders():
    if not os.path.exists("data/casino"):
        print("Creating data/casino folder...")
        os.makedirs("data/casino")


def check_files():

    f = "data/casino/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default casino's settings.json...")
        dataIO.save_json(f, {})

    f = "data/casino/bank.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty bank.json...")
        dataIO.save_json(f, {})


def setup(bot):
    global logger
    check_folders()
    check_files()
    logger = logging.getLogger("red.casino")
    if logger.level == 0:
        # Prevents the logger from being loaded again in case of module reload
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(
            filename='data/casino/casino.log', encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(message)s', datefmt="[%d/%m/%Y %H:%M]"))
        logger.addHandler(handler)
    bot.add_cog(Casino(bot))
