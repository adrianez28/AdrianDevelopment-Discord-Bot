#AdrianDevelopment Bot

import discord
from discord.ext import commands, tasks
import json, os
import yaml, asyncio

from core import database

config = json.loads(open("config.json").read())

def save_panel_id(panel_type, message_id):
    try:
        with open("db/data.yaml", "r") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        data = {}
    data[panel_type] = message_id
    with open("db/data.yaml", "w") as f:
        yaml.dump(data, f)

def load_panel_ids():
    try:
        with open("db/data.yaml", "r") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

class BotsPanelView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction = None, option=None, bot=None):
        super().__init__(timeout=None)
        self.interaction = interaction
        self.option = option
        self.db = database.Database()
        self.bot = bot

    @discord.ui.button(label="Contact", style=discord.ButtonStyle.primary)
    async def contact_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        select_menu = discord.ui.Select(
            placeholder="Select a support option",
            options=[
                discord.SelectOption(label="Paypal", value="paypal"),
                discord.SelectOption(label="Litecoin", value="litecoin"),
            ]
        )

        async def select_callback(select_interaction: discord.Interaction):
            value = select_menu.values[0]
            user = select_interaction.user.id
            self.db.add_user(user)
            self.db.add_active_conversation(user)

            if value == "paypal":
                embed_to_user = discord.Embed(
                    title="You have contacted",
                    description=f"You have contacted to <@{config['bot_config']['owner_id']}>.\n\n**Payment Method:** Paypal\n\nPlease wait for a response.\n\n Note: \n > You can send a message with /send_message.",
                    color=discord.Color.green()
                )
                await select_interaction.user.send(embed=embed_to_user)
                log_embed = discord.Embed(
                    title="User Contacted (Paypal)",
                    description=f"User <@{user}> has contacted for Paypal support.",
                    color=discord.Color.blue()
                )
            elif value == "litecoin":
                embed_to_user = discord.Embed(
                    title="You have contacted",
                    description=f"You have contacted to <@{config['bot_config']['owner_id']}>.\n\n**Payment Method:** Litecoin\n\nPlease wait for a response.\n\n Note: \n > You can send a message with /send_message.",
                    color=discord.Color.green()
                )
                await select_interaction.user.send(embed=embed_to_user)
                log_embed = discord.Embed(
                    title="User Contacted (Litecoin)",
                    description=f"User <@{user}> has contacted for Litecoin support.",
                    color=discord.Color.blue()
                )
            
            log_channel_id = config['bot_config']['log_channel_id']
            log_channel = None
            if self.bot:
                guild = self.bot.get_guild(config['bot_config']['server_id'])
                if guild:
                    log_channel = guild.get_channel(log_channel_id)
            
            if log_channel:
                await log_channel.send(embed=log_embed)
            
            await select_interaction.response.send_message("✅ Contact request sent successfully!", ephemeral=True)

        select_menu.callback = select_callback

        view = discord.ui.View()
        view.add_item(select_menu)

        embed = discord.Embed(
            title="Support Options",
            description="Please select a payment method from the dropdown menu below:",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class Bot:

    def __init__(self):

        #Bot config
        self.token = config['bot_config']['token']
        self.prefix = config['bot_config']['prefix']
        self.owner_id = config['bot_config']['owner_id']
        self.server_id = config['bot_config']['server_id']
        self.activity = config['bot_config']['activity']
        self.log_channel_id = config['bot_config']['log_channel_id']
        self.channel_discord_bots = config['bot_config']['discord_bots_panel_channel']
        self.channel_projects = config['bot_config']['projects_panel_channel']
        self.discord_customer_role = config['bot_config']['discord_customer_role']
        self.projects_customer_role = config['bot_config']['projects_customer_role']

        #Payment config
        self.paypal_email = config['payment_config']['paypal']['email']
        self.litecoin_address = config['payment_config']['litecoin']['address']

        #Panel state variables
        self.discord_bots_panel_sent = False
        self.projects_panel_sent = False
        self.current_discord_bots_message = None
        self.current_projects_message = None

        self.panel_task = None

        #DB
        self.db = database.Database()

        #Clear terminal and run bot
        os.system('cls')
        self.run()

    async def auto_refresh_panel(self, interaction, panel_type, message_id, embed, channel_id):

        while True:
            try:
                channel1 = self.bot.get_channel(channel_id)
                try:
                    message = await channel1.fetch_message(message_id)
                    await message.delete()
                    print(f"Panel {panel_type} deleted after 40 segundos")
                except discord.NotFound:
                    print(f"Panel {panel_type} message not found (may have been deleted already)")
                except Exception as e:
                    print(f"Error deleting {panel_type} panel message: {e}")

                await asyncio.sleep(2)

                channel = self.bot.get_channel(channel_id)
                if channel:
                    new_view = BotsPanelView(interaction, option=panel_type, bot=self.bot)
                    new_message = await channel.send(embed=embed, view=new_view)

                    message_id = new_message.id
                    if panel_type == "discord_bots_panel":
                        self.current_discord_bots_message = message_id
                        save_panel_id("discord_bots_panel", message_id)
                    elif panel_type == "projects_panel":
                        self.current_projects_message = message_id
                        save_panel_id("projects_panel", message_id)

                    print(f"New {panel_type} panel created")

            except Exception as e:
                print(f"Error refreshing {panel_type} panel: {e}")
                
            await asyncio.sleep(40)

    def commands(self):
        
        #Commands
        @self.bot.event
        async def on_ready():
            await self.tree.sync()
            await self.tree.sync(guild=discord.Object(id=self.server_id))
            await self.bot.change_presence(activity=discord.activity.Game("AdrianDevelopment", extra={"large_image": "https://cdn.discordapp.com/icons/1408846450494013513/e8e637a9b5b9e01b767f68442d561049.png?size=4096"}))

            print(f"Bot {self.bot.user} is ready!")

        @self.tree.command(name="send_message_to_owner", description="Send a message to the owner.")
        async def send_message(interaction: discord.Interaction, message: str, screenshot: discord.Attachment = None):

            if interaction.channel.type != discord.ChannelType.private:
                await interaction.response.send_message("This command can only be used in direct messages with the bot.", ephemeral=True)
                return

            user = self.db.get_active_conversations_user(interaction.user.id)
            if user == False:
                await interaction.response.send_message("You don't have an active conversation.", ephemeral=True)
                return

            if not message:
                await interaction.response.send_message("You must provide a message to send.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="New Message from User",
                description=message,
                color=discord.Color.blue()
            )
            if screenshot:
                embed.set_image(url=screenshot.url)

            log_embed = discord.Embed(
                title="Message Sent to Owner",
                description=f"Message sent to the owner: {message}",
                color=discord.Color.green()
            )

            owner = await self.bot.fetch_user(self.owner_id)
            if owner:
                await owner.send(embed=embed)
            await self.bot.get_channel(self.log_channel_id).send(embed=log_embed)
            await interaction.response.send_message("Message sent to the owner.", ephemeral=True)

        @self.tree.command(name="send-discord-bots-panel", description="Sends the Discord Bots Panel embed.", guild=discord.Object(id=self.server_id))
        async def send_discord_bots_panel(interaction: discord.Interaction):
            if int(interaction.user.id) != int(self.owner_id):
                await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
                return

            if int(interaction.channel.id) != int(self.channel_discord_bots):
                await interaction.response.send_message(f"This command can only be used in the <#{self.channel_discord_bots}> channel.", ephemeral=True)
                return

            self.discord_bots_panel_sent = True

            embed = discord.Embed(
                title="Discord Bots Panel",
                description="Do you need a discord bot? Contact us, tell us what you need and we'll create it for you.",
                color=discord.Color.blue()
            )
            view = BotsPanelView(interaction, "Discord Bots", self.bot)
            msg = await interaction.channel.send(embed=embed, view=view)
            
            self.current_discord_bots_message = msg.id
            
            self.bot.loop.create_task(self.auto_refresh_panel(interaction, "discord_bots_panel", self.current_discord_bots_message, embed, view, self.channel_discord_bots))
            
            await interaction.response.send_message("Discord Bots Panel sent with auto-refresh enabled.", ephemeral=True)

        @self.tree.command(name="send-projects-panel", description="Sends the Projects Panel embed.", guild=discord.Object(id=self.server_id))
        async def send_projects_panel(interaction: discord.Interaction):
            if int(interaction.user.id) != int(self.owner_id):
                await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
                return

            if int(interaction.channel.id) != int(self.channel_projects):
                await interaction.response.send_message(f"This command can only be used in the <#{self.channel_projects}> channel.", ephemeral=True)
                return

            self.projects_panel_sent = True

            embed = discord.Embed(
                title="Projects Panel",
                description="Do you need a programming project? Contact us, tell us what you need and we'll create it for you.",
                color=discord.Color.blue()
            )
            view = BotsPanelView(interaction, "Projects", self.bot)
            msg = await interaction.channel.send(embed=embed, view=view)
            
            self.current_projects_message = msg.id

            self.bot.loop.create_task(self.auto_refresh_panel(interaction, "projects_panel", self.current_projects_message, embed, view, self.channel_projects))
            
            await interaction.response.send_message("Projects Panel sent with auto-refresh enabled.", ephemeral=True)

        @self.tree.command(name="send_message_to_user", description="Send a message to the user.", guild=discord.Object(id=self.server_id))
        async def send_message(interaction: discord.Interaction, discord_id: discord.Member, message: str, screenshot: discord.Attachment = None):
            if int(interaction.user.id) != int(self.owner_id):
                await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
                return

            user = discord_id

            if not message:
                await interaction.response.send_message("You must provide a message to send.", ephemeral=True)
                return

            embed = discord.Embed(
                title="New Message from Owner",
                description=message,
                color=discord.Color.blue()
            )
            if screenshot:
                embed.set_image(url=screenshot.url)

            log_embed = discord.Embed(
                title="Message Sent to User",
                description=f"Message sent to {user.name}: {message}",
                color=discord.Color.green()
            )

            await user.send(embed=embed)
            await self.bot.get_channel(self.log_channel_id).send(embed=log_embed)
            await interaction.response.send_message("Message sent.", ephemeral=True)

        @self.tree.command(name="delivery", description="Delivery the product.", guild=discord.Object(id=self.server_id))
        async def delivery(interaction: discord.Interaction, user: discord.User, link: str, option: str, amount: int, instructions: str):
            if int(interaction.user.id) != int(self.owner_id):
                await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
                return
            
            if instructions is None:
                await interaction.response.send_message("You must provide instructions for the delivery.", ephemeral=True)
                return

            if not link:
                await interaction.response.send_message("You must provide a delivery link.", ephemeral=True)
                return

            embed = discord.Embed(
                title=f"Delivery {option}",
                description=f"Delivery link: {link} \n\n**Instructions**: {instructions}",
                color=discord.Color.blue()
            )

            log_embed = discord.Embed(
                title="Delivery Sent",
                description=f"Delivery link sent to {user.name}: {link}",
                color=discord.Color.green()
            )

            await user.send(embed=embed)
            await self.bot.get_channel(self.log_channel_id).send(embed=log_embed)
            await interaction.response.send_message("Delivery sent.", ephemeral=True)

            self.db.remove_active_conversation(user.id)
            self.db.add_purchase(user.id, amount)

            if option.lower() == "discord bots":
                await user.add_roles(discord.utils.get(interaction.guild.roles, id=self.discord_customer_role))
            elif option.lower() == "projects":
                await user.add_roles(discord.utils.get(interaction.guild.roles, id=self.projects_customer_role))

        @self.tree.command(name="stats", description="Get your stats.", guild=discord.Object(id=self.server_id))
        async def stats(interaction: discord.Interaction):

            user = interaction.user.id

            user_stats = self.db.get_user(user)
            if user_stats == None:
                await interaction.response.send_message("No stats found for you.", ephemeral=True)
                return

            embed = discord.Embed(
                title="Your Stats",
                description=f"> Purchases: {user_stats['purchases']}\n > Spent Money: {user_stats['spent_money']}",
                color=discord.Color.blue()
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        @self.tree.command(name="send_payment", description="Create invoice", guild=discord.Object(id=self.server_id))
        async def send_payment(interaction: discord.Interaction, user: discord.User, payment_method: str):
            if int(interaction.user.id) != int(self.owner_id):
                await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
                return

            if payment_method.lower() not in ["paypal", "litecoin"]:
                await interaction.response.send_message("Invalid payment method.", ephemeral=True)
                return

            if payment_method.lower() == "paypal":
                embed = discord.Embed(
                    title="New Invoice",
                    description=f"Invoice created for {user.name} using PayPal.",
                    color=discord.Color.blue()
                )

                dm_embed = discord.Embed(
                    title="New Invoice",
                    description=f"You have a new invoice using PayPal, Email: {self.paypal_email}",  # Corregido
                    color=discord.Color.blue()
                )

                log_embed = discord.Embed(
                    title="New Invoice",
                    description=f"Invoice created for {user.name} using PayPal.",
                    color=discord.Color.blue()
                )

            elif payment_method.lower() == "litecoin":
                embed = discord.Embed(
                    title="New Invoice",
                    description=f"Invoice created for {user.name} using Litecoin.",
                    color=discord.Color.blue()
                )

                dm_embed = discord.Embed(
                    title="New Invoice",
                    description=f"You have a new invoice using Litecoin, Address: {self.litecoin_address} when you have sent the money please send screenshot.",
                    color=discord.Color.blue()
                )

                log_embed = discord.Embed(
                    title="New Invoice",
                    description=f"Invoice created for {user.name} using Litecoin.",
                    color=discord.Color.blue()
                )

            await user.send(embed=dm_embed)
            await self.bot.get_channel(self.log_channel_id).send(embed=log_embed)  # Corregido
            await interaction.response.send_message(embed=embed, ephemeral=True)

    def run(self):

        self.bot = commands.Bot(command_prefix=self.prefix, intents=discord.Intents.all())
        self.tree = self.bot.tree
        self.commands()
        self.bot.run(self.token)

if __name__ == "__main__":
    bot = Bot()
