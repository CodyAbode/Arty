import os
import json
import random
import secrets
from typing import List
import asyncio
import logging

import disnake
from disnake import guild
from disnake.ext import commands

log_formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('arty')
file_handler = logging.FileHandler('arty_log.txt')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

logger.info('Initializing...')

secrets_file = 'secrets.json'
user_data_file = 'user_data.json'
store_data_file = 'store_data.json'
media_directory = 'media'
main_color = disnake.Color.from_rgb(14, 0, 89)
bot_version = '3.0.0'
moderator = disnake.Permissions(moderate_members=True)

if os.path.exists(secrets_file):
        with open(secrets_file) as file:
            secrets = json.load(file)
        bot_token = secrets['bot_token']
        guild_id = secrets['guild_id']
        general_chanel = secrets['general_chanel']
        steam_api_key = secrets['steam_api_key']
        news_channel = secrets['news_channel']
else:
    error_msg = f'Could not find {secrets_file}'
    logger.error(error_msg)
    raise Exception(error_msg)

def load_user_data():
    if os.path.exists(user_data_file):
        with open(user_data_file) as file:
            return json.load(file)
    else:
        return {}

def save_user_data(user_data):
    with open(user_data_file, 'w') as file:
        json.dump(user_data, file, indent=4)

def ensure_user_data(user: disnake.user):
    user_data = load_user_data()
    if not str(user.id) in user_data:
        user_data[str(user.id)] = {
            'tickets': 0,
            'tickets_earned': 0,
            'inventory': [],
        }
    return user_data

def emoji(name):
    for emoji in bot.emojis:
        if name == emoji.name:
            return f'<:{name}:{emoji.id}>'
    return f':{name}:'

def bold(text):
    return f'**{text}**'

def load_store_data():
    if os.path.exists(store_data_file):
        with open(store_data_file) as file:
            return json.load(file)
    else:
        raise Exception('Unable to find the store data file')

def hex_to_rgb(hex):
    return tuple(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

intents = disnake.Intents.default()
intents.presences = False
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned,
    test_guilds=[guild_id],
    sync_commands_debug=True,
    intents=intents
    )

@bot.event
async def on_ready():
    logger.info(f'Ready! Bot version {bot_version}. Logged in as {bot.user} (ID: {bot.user.id})')

@bot.slash_command(default_member_permissions=moderator)
async def ping(inter):
    """Check bot availability and latency."""
    logger.info(f'{inter.author} used ping()')
    await inter.response.send_message(f'Pong! ({inter.client.latency*1000}ms)')

@bot.slash_command(default_member_permissions=moderator)
async def message(inter, channel: disnake.TextChannel, message: str):
    """
    Send a message in a specified channel.

    Parameters
    ----------
    channel: The channel to send the message in.
    message: The message to send.
    """
    logger.info(f'{inter.author} used /message(channel: {channel.name}, message: {message})')
    await channel.send(message)
    await inter.response.send_message(f'Message sent to <#{channel.id}>.')

@bot.slash_command(default_member_permissions=moderator)
async def dispense(inter, amount: int, user: disnake.User):
    """
    Give tickets to a user.

    Parameters
    ----------
    amount: The number of tickets to give.
    user: The member to give tickets to.
    """
    logger.info(f'{inter.author} used /dispense(amount: {amount}, user: {user.display_name})')
    user_data = ensure_user_data(user)
    user_data[str(user.id)]['tickets'] += amount
    user_data[str(user.id)]['tickets_earned'] += amount
    save_user_data(user_data)
    await inter.response.send_message(f"Dispensed {amount} {emoji('ArcadeTicket')} to <@{str(user.id)}>.")

@bot.slash_command()
async def ticket(inter):
    pass

@ticket.sub_command()
async def balance(inter):
    """
    Displays your ticket balance, and how many you've earned.
    """
    logger.info(f'{inter.author} used /ticket balance()')
    user_data = ensure_user_data(inter.author)
    tickets = user_data[str(inter.author.id)]['tickets']
    tickets_earned = user_data[str(inter.author.id)]['tickets_earned']
    await inter.response.send_message(f"You have a balance of {tickets} {emoji('ArcadeTicket')} and have earned {tickets_earned} {emoji('ArcadeTicket')}.", ephemeral=True)

@ticket.sub_command()
async def leaderboard(inter, quiet: bool = True):
    """
    Displays how many tickets everyone has earned.

    Parameters
    ----------
    quiet: Hides the reponse, so only you can see it.
    """
    logger.info(f'{inter.author} used /ticket leaderboard(quiet: {quiet})')
    user_data = load_user_data()
    sorted_data = {k: v for k, v in sorted(user_data.items(), key=lambda item: item[1]['tickets_earned'], reverse=True)}
    leaderboard_embed = disnake.Embed(
        title='Leaderboard',
        type='rich',
        color=main_color
    )
    users = ''
    tickets = ''
    for user_id, user_data in sorted_data.items():
        #user = await bot.fetch_user(user_id)
        user = await bot.guilds[0].fetch_member(user_id)
        ticket = str(user_data['tickets_earned'])
        users += f'{user.nick or user.global_name or user.name}\n'
        tickets += f"{ticket} {emoji('ArcadeTicket')}\n"
    leaderboard_embed.add_field(name='Members', value=users)
    leaderboard_embed.add_field(name='Tickets Earned', value=tickets)
    await inter.response.send_message(embed=leaderboard_embed, ephemeral=quiet)

@bot.slash_command()
async def inventory(inter):
    """Display your items."""
    logger.info(f'{inter.author} used /inventory()')
    user_data = ensure_user_data(inter.author)
    inventory = user_data[str(inter.author.id)]['inventory']
    description = ''
    if len(inventory) == 0:
        empty_responses = [
            f"{emoji('dog')} Wow, such empty!",
            f"{emoji('trophy')} This is where I'd put my trophy, if I had one!",
            f"{emoji('spider_web')} There is nothing here.",
            ]
        description = random.choice(empty_responses)
    else:
        for index, item in enumerate(inventory):
                item_name = bold(inventory[index]['name'])
                item_emoji = emoji(inventory[index]['emoji'])
                description += f'\n{index + 1}) {item_emoji} {item_name}'
    description += f"\n Tickets: {user_data[str(inter.author.id)]['tickets']} {emoji('ArcadeTicket')}"
    inventory_embed = disnake.Embed(
        title='Inventory',
        type='rich',
        description=description,
        color=main_color
    )
    await inter.response.send_message(embed=inventory_embed, ephemeral=True)

async def autocomplete_items(inter, string: str) -> List[str]:
    user_data = ensure_user_data(inter.author)
    inventory = user_data[str(inter.author.id)]['inventory']
    item_names = []
    for item in inventory:
        item_names.append(item['name'])
    return item_names

class ComplimentVoucherView(disnake.ui.View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label='Send', style=disnake.ButtonStyle.blurple, row=0)
    async def send(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        button.disabled = True
        await inter.response.send_modal(
            title='Compliment Voucher',
            custom_id='compliment-voucher',
            components=[
                disnake.ui.TextInput(
                label='User',
                custom_id='user',
                style=disnake.TextInputStyle.short,
                placeholder='The user to send the compliment to...',
                max_length=32
                )
            ]
        )

        try:
            modal_inter: disnake.ModalInteraction = await bot.wait_for(
                'modal_submit',
                check=lambda i: i.custom_id == 'compliment-voucher' and i.author.id == inter.author.id,
                timeout=300,
            )
        except asyncio.TimeoutError:
            return
        
        user = modal_inter.text_values['user']
        member = bot.guilds[0].get_member_named(user)
        if not member:
            await modal_inter.response.send_message(f"Could not find a member named {bold(user)}.", ephemeral=True)
            logger.debug(f'{inter.author} tried to send a compliment to a non-existant member named {member.display_name}')
            self.stop()
            return
        compliments = [
            f"I'm glad you're here, <@{member.id}>.",
            f"9 out of 10 doctors agree you are beautiful, <@{member.id}>.",
            f"You're the best, <@{member.id}>.",
            f"You are a good friend, <@{member.id}>.",
            f"This server wouldn't be the same without you, <@{member.id}>.",
            f"This is the picture I got when I looked up *charming* in the dictionary: {member.avatar.url}",
        ]
        await bot.guilds[0].get_channel(general_chanel).send(random.choice(compliments))
        user_data = load_user_data()
        for index, item in enumerate(user_data[str(inter.author.id)]['inventory']):
            if item['name'] == 'Arty Compliment Voucher':
                user_data[str(inter.author.id)]['inventory'].pop(index)
                save_user_data(user_data)
                break
        await modal_inter.response.send_message(f"Sent compliment to {bold(member.display_name)}.", ephemeral=True)
        logger.info(f'{inter.author} sent a compliment to {member.display_name}')
        self.stop()

class CapsuleView(disnake.ui.View):
    def __init__(self, capsule: str):
        self.capsule = capsule
        super().__init__()

    @disnake.ui.button(label='Open', style=disnake.ButtonStyle.blurple, row=0)
    async def open(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        user_data = ensure_user_data(inter.author)
        inventory = user_data[str(inter.author.id)]['inventory']
        inventory_item_names = []
        for inventory_item in inventory:
            inventory_item_names.append(inventory_item['name'])
        if not self.capsule in inventory_item_names:
            await inter.send(f"Could not find {emoji('Capsule')} {bold(self.capsule)} in your inventory.", ephemeral=True)
            logger.debug(f'{inter.author} tried to open non-existant capsule {self.capsule}')
            return
        open_options = ['pix', 'tickets', 'store']
        result = random.choices(open_options, weights=[10, 1, 1], k=1)[0]
        if result == 'pix':
            pix_types = ['basic', 'mask', 'furry', 'grated', 'combined', 'linear', 'wild', 'thorny', 'poisonous', 'mystical', 'elemental', 'ancient']
            type_weights = [12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
            pix_type_result = random.choices(pix_types, weights=type_weights, k=1)[0]
            pix_list = os.listdir(os.path.join(media_directory, 'Pix', pix_type_result))
            image = os.path.join('Pix', pix_type_result, random.choice(pix_list))
            pix_item = {
                'name': f"{pix_type_result.capitalize()} Pix#{str(random.randint(0, 9999)).rjust(4, '0')}",
                'emoji': 'Capsule',
                'image': image,
                'description': f"A creature known as a pix. This is a {pix_type_result} pix. It was found by {inter.author.display_name}.",
                'tags': {'pix': pix_type_result}
            }
            user_data[str(inter.author.id)]['inventory'].append(pix_item)
            content = f"You got {emoji(pix_item['emoji'])} {bold(pix_item['name'])}!"
            log_content = f"{pix_item['name']}"
        elif result == 'tickets':
            amount = random.randint(10, 80)
            user_data[str(inter.author.id)]['tickets'] += amount
            content = f"You got {amount} {emoji('ArcadeTicket')}!"
            log_content = f"{amount} tickets"
        elif result == 'store':
            store_data = load_store_data()
            store_items = []
            store_prices = []
            for listing in store_data:
                store_items.append(listing['item'])
                store_prices.append(listing['price'])
            while True:
                store_result = random.choices(store_items, weights=store_prices, k=1)[0]
                if not 'unique' in store_result['tags'].keys():
                    store_result['name'] += f"#{str(random.randint(0, 9999)).rjust(4, '0')}"
                if not store_result['name'] in inventory_item_names:
                    user_data[str(inter.author.id)]['inventory'].append(store_result)
                    content = f"You got {emoji(store_result['emoji'])} {bold(store_result['name'])}!"
                    log_content = f"{store_result['name']}"
                    break
        for index, item in enumerate(user_data[str(inter.author.id)]['inventory']):
            if item['name'] == self.capsule:
                user_data[str(inter.author.id)]['inventory'].pop(index)
                save_user_data(user_data)
                break
        await inter.send(content, ephemeral=True)
        logger.info(f'{inter.author} opened {self.capsule} and got {log_content}')

class ColorRoleView(disnake.ui.View):
    def __init__(self, color: str):
        self.color = color
        super().__init__()

    @disnake.ui.button(label='Toggle Role', style=disnake.ButtonStyle.blurple, row=0)
    async def toggle(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.color == 'custom':
            await inter.response.send_modal(
                    title='Custom Color Role',
                    custom_id='custom-color-role',
                    components=[
                        disnake.ui.TextInput(
                        label='Hex Color',
                        custom_id='hex-color',
                        style=disnake.TextInputStyle.short,
                        placeholder='000000',
                        min_length=6,
                        max_length=6
                        )
                    ]
                )
            
            try:
                modal_inter: disnake.ModalInteraction = await bot.wait_for(
                    'modal_submit',
                    check=lambda i: i.custom_id == 'custom-color-role' and i.author.id == inter.author.id,
                    timeout=300,
                )
            except asyncio.TimeoutError:
                return
            
            hex_color = modal_inter.text_values['hex-color']
            if not hex_color:
                await modal_inter.response.send_message("No color input.", ephemeral=True)
                self.stop()
                return
            
            self.color = hex_color
            await modal_inter.response.send_message(f"Chosen color: {hex_color.upper()}.", ephemeral=True)
            self.stop()
            
        role_name = f"Color: {self.color.upper()}"
        guild_role_names = []
        for role in bot.guilds[0].roles:
            guild_role_names.append(role.name)
        if not role_name in guild_role_names:
            try:
                rgb_color = hex_to_rgb(self.color)
            except ValueError:
                await inter.send(f"{self.color.upper()} is not a valid hex color.", ephemeral=True)
                logger.info(f'{inter.author} submitted invalid hex color {self.color.upper()}')
                return
            await bot.guilds[0].create_role(
                name=role_name,
                color=disnake.Color.from_rgb(rgb_color[0], rgb_color[1], rgb_color[2])
            )
            for role in bot.guilds[0].roles:
                if role.name == role_name:
                    await bot.guilds[0].edit_role_positions(
                        positions={role: len(bot.guilds[0].roles) - 2}
                        )
                    break
            logger.info(f'Created color role {role_name}')
        for role in bot.guilds[0].roles:
            if role.name == role_name:
                color_role = role
                break
        user_roles_names = []
        for role in inter.author.roles:
            user_roles_names.append(role.name)
        if role_name in user_roles_names:
            await inter.author.remove_roles(color_role)
            await inter.send(f"Role {bold(role_name)} removed.", ephemeral=True)
            logger.info(f'{inter.author} removed color role {role_name}')
            if len(color_role.members) == 0:
                await color_role.delete()
                logger.info(f'Removed empty color role {role_name}')
            return
        else:
            for role in inter.author.roles:
                if str(role.name).startswith("Color: "):
                    await inter.author.remove_roles(role)
                    if len(role.members) == 0:
                        await color_role.delete()
                        logger.info(f'Removed empty color role {role_name}')
            await inter.author.add_roles(color_role)
            await inter.send(f"Role {bold(role_name)} added.", ephemeral=True)
            logger.info(f'{inter.author} added color role {role_name}')
            return

@bot.slash_command()
async def item(inter):
    pass

@item.sub_command()
async def show(inter, item: str = commands.Param(autocomplete=autocomplete_items)):
    """
    Display the details of an item.

    Parameters
    ----------
    item: The item to inspect.
    """
    logger.info(f'{inter.author} used /item show(item: {item})')
    user_data = ensure_user_data(inter.author)
    inventory = user_data[str(inter.author.id)]['inventory']
    inventory_item = next((search_item for search_item in inventory if search_item['name'] == item), None)
    if not inventory_item:
        await inter.response.send_message(f"Could not find {bold(item)} in your inventory.", ephemeral=True)
        return
    item_show_embed = disnake.Embed(
        title=f"{emoji(inventory_item['emoji'])} {inventory_item['name']}",
        type='rich',
        description=inventory_item['description'],
        color=main_color,
    )
    if inventory_item['image']:
        filepath = os.path.join(media_directory, inventory_item['image'])
        with open(filepath, 'rb') as file:
            item_show_embed.set_image(file=disnake.File(file))
    tags = ', '.join(list(inventory_item['tags'].keys()))
    item_show_embed.set_footer(text=f"tags: {tags or 'None'}")
    if 'compliment-voucher' in inventory_item['tags'].keys():
        view = ComplimentVoucherView()
        await inter.response.send_message(embed=item_show_embed, view=view, ephemeral=True)
        return
    elif 'capsule' in inventory_item['tags'].keys():
        view = CapsuleView(item)
        await inter.response.send_message(embed=item_show_embed, view=view, ephemeral=True)
        return
    elif 'color-role' in inventory_item['tags'].keys():
        view = ColorRoleView(inventory_item['tags']['color-role'])
        await inter.response.send_message(embed=item_show_embed, view=view, ephemeral=True)
        return
    await inter.response.send_message(embed=item_show_embed, ephemeral=True)

@item.sub_command()
async def send(
    inter,
    user: disnake.Member,
    item: str = commands.Param(autocomplete=autocomplete_items),
    ):
    """
    Send an item to another user.

    Parameters
    ----------
    user: The user to send the item to.
    item: The item to send.
    """
    logger.info(f'{inter.author} used /item send(user: {user.name} item: {item})')
    user_data = ensure_user_data(user)
    inventory = user_data[str(inter.author.id)]['inventory']
    inventory_item = next((search_item for search_item in inventory if search_item['name'] == item), None)
    if not inventory_item:
        await inter.response.send_message(f"Could not find {bold(item)} in your inventory.", ephemeral=True)
        logger.info(f"Could not find {item} in {inter.author}'s inventory")
        return
    if user.bot:
        await inter.response.send_message(f"You can not send items to bots.", ephemeral=True)
        logger.info(f'{inter.author} tried to send an item to a bot ({user.name})')
        return
    if user.id == inter.author.id:
        await inter.response.send_message(f"You can not send items to yourself.", ephemeral=True)
        logger.info(f'{inter.author} tried to send an item to themself')
        return
    if 'unique' in inventory_item['tags'].keys():
        giftee_inventory = user_data[str(user.id)]['inventory']
        giftee_inventory_item_names = []
        for g_item in giftee_inventory:
            giftee_inventory_item_names.append(g_item['name'])
        if item in giftee_inventory_item_names:
            await inter.response.send_message(f"{user.nick or user.global_name or user.name} already has {emoji(inventory_item['emoji'])} {bold(inventory_item['name'])}.", ephemeral=True)
            logger.info(f'{inter.author} tried to send {item} to {user.name}, but they already have it')
            return
    user_data[str(inter.author.id)]['inventory'].remove(inventory_item)
    user_data[str(user.id)]['inventory'].append(inventory_item)
    save_user_data(user_data)
    await inter.response.send_message(f"Sent {emoji(inventory_item['emoji'])} {bold(inventory_item['name'])} to {user.nick or user.global_name or user.name}.", ephemeral=True)
    logger.info(f'{inter.author} sent {item} to {user.name}')
    dm = user.dm_channel or await user.create_dm()
    await dm.send(f"{inter.author.nick or inter.author.global_name or inter.author.name} ({inter.author.name}) sent you {emoji(inventory_item['emoji'])} {bold(inventory_item['name'])}!")
    return

@bot.slash_command()
async def store(inter):
    pass

@store.sub_command()
async def display(inter):
    """
    Display the ticket store.
    """
    logger.info(f'{inter.author} used /store display()')
    store_data = load_store_data()
    store_display_embed = disnake.Embed(
        title=f"Ticket Store",
        type='rich',
        color=main_color,
    )
    for listing in store_data:
        store_display_embed.add_field(
            name = f"{emoji(listing['item']['emoji'])} {bold(listing['item']['name'])}",
            value = f"{listing['item']['description']}\nPrice: {listing['price']} {emoji('ArcadeTicket')}",
            inline = False
        )
    store_display_embed.set_footer(text="Use '/store buy {item}' to purchase.\nItems and prices subject to change.")
    await inter.response.send_message(embed=store_display_embed, ephemeral=True)

async def autocomplete_store_items(inter, string: str) -> List[str]:
    store_data = load_store_data()
    item_names = []
    for listing in store_data:
        item_names.append(listing['item']['name'])
    return item_names

@store.sub_command()
async def buy(inter, item: str = commands.Param(autocomplete=autocomplete_store_items)):
    """
    Purchase an item from the ticket store.

    Parameters
    ----------
    item: The item to buy.
    """
    logger.info(f'{inter.author} used /store display(item: {item})')
    if not item:
        await inter.response.send_message('You must choose an item to buy.', ephemeral=True)
        return
    user_data = ensure_user_data(inter.author)
    inventory = user_data[str(inter.author.id)]['inventory']
    if len(inventory) >= 25:
        await inter.response.send_message('Your inventory is full!', ephemeral=True)
        return
    store_data = load_store_data()
    for listing in store_data:
        if listing['item']['name'] == item:
            if user_data[str(inter.author.id)]['tickets'] >= listing['price']:
                inventory_item_names = []
                for inventory_item in inventory:
                    inventory_item_names.append(inventory_item['name'])
                if not 'unique' in listing['item']['tags'].keys():
                    listing['item']['name'] += f"#{str(random.randint(0, 9999)).rjust(4, '0')}"
                if listing['item']['name'] in inventory_item_names:
                    await inter.response.send_message(f"You already have {emoji(listing['item']['emoji'])} {bold(listing['item']['name'])} in your inventory.", ephemeral=True)
                    return
                user_data[str(inter.author.id)]['tickets'] -= listing['price']
                user_data[str(inter.author.id)]['inventory'].append(listing['item'])
                save_user_data(user_data)
                await inter.response.send_message(f"You purchased {emoji(listing['item']['emoji'])} {bold(listing['item']['name'])}! Your new balance is {user_data[str(inter.author.id)]['tickets']} {emoji('ArcadeTicket')}.", ephemeral=True)
                return
            else:
                await inter.response.send_message(f"You don't have enough tickets for {emoji(listing['item']['emoji'])} {bold(listing['item']['name'])}.", ephemeral=True)
                return
    await inter.response.send_message(f"Could not find {bold(item)} in the store.", ephemeral=True)

bot.run(bot_token)