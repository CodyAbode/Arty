import os
import json
import random
import secrets
import asyncio
import logging
from typing import List
import datetime

import disnake
from disnake.ext import commands

import dice_express

datetime_format = '%Y-%m-%d %H:%M:%S'
log_formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s', datefmt=datetime_format)
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
bot_version = '3.3.0'
moderator = disnake.Permissions(moderate_members=True)

if os.path.exists(secrets_file):
        with open(secrets_file) as file:
            secrets = json.load(file)
        bot_token = secrets['bot_token']
        guild_id = secrets['guild_id']
        general_channel = secrets['general_channel']
        mod_channel = secrets['mod_channel']
else:
    error_msg = f'Could not find {secrets_file}'
    logger.error(error_msg)
    raise Exception(error_msg)

class InventoryError(Exception):
    pass

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

def remove_inventory_item(user: disnake.user, item_id: str):
    user_data = load_user_data()
    for index, item in enumerate(user_data[str(user.id)]['inventory']):
        if item['id'] == item_id:
            unstacked = False
            if 'data' in item:
                if 'quantity' in item['data']:
                    if item['data']['quantity'] >= 2:
                        user_data[str(user.id)]['inventory'][index]['data']['quantity'] -= 1
                        unstacked = True
            if not unstacked:
                user_data[str(user.id)]['inventory'].pop(index)
            save_user_data(user_data)
            break

def add_inventory_item(user: disnake.user, item: dict):
    user_data = ensure_user_data(user)
    inventory = user_data[str(user.id)]['inventory']
    if len(inventory) >= 25:
        error = f'Users inventory is full.'
        logger.warning(error)
        raise InventoryError(error)
    if not any(tag in ['unique', 'stackable'] for tag in item['tags']):
        uid = f"#{str(random.randint(0, 9999)).rjust(4, '0')}"
        item['name'] += uid
        item['id'] += uid
    stacked = False
    for inventory_index, inventory_item in enumerate(inventory):
        if item['id'] == inventory_item['id']:
            if 'stackable' in item['tags']:
                if not 'data' in item:
                    item['data'] = {}
                if not 'quantity' in item['data']:
                    item['data']['quantity'] = 1
                if not 'data' in user_data[str(user.id)]['inventory'][inventory_index]:
                    user_data[str(user.id)]['inventory'][inventory_index]['data'] = {}
                if not 'quantity' in user_data[str(user.id)]['inventory'][inventory_index]['data']:
                    user_data[str(user.id)]['inventory'][inventory_index]['data']['quantity'] = 1
                user_data[str(user.id)]['inventory'][inventory_index]['data']['quantity'] += item['data']['quantity']
                stacked = True
                break
            else:
                error = f'User already has unique item {item['name']} in their inventory.'
                logger.warning(error)
                raise InventoryError(error)
    if not stacked:
        user_data[str(user.id)]['inventory'].append(item)
    save_user_data(user_data)

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
    
def save_store_data(store_data):
    with open(store_data_file, 'w') as file:
        json.dump(store_data, file, indent=4)

def hex_to_rgb(hex):
    return tuple(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

json_file = 'schedule.json'

async def scheduled_actions():
    try:
        # Read last run time from JSON file
        last_run_time = None
        now = datetime.datetime.now()
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
                last_run_time_str = data.get('last_run_time')
                if last_run_time_str:
                    last_run_time = datetime.datetime.fromisoformat(last_run_time_str)
                    print(f'Last scheduled action performed at {last_run_time}.')
        else:
            # If no JSON file exists, set last_run_time to now
            print(f'No previous scheduled action found.')
            last_run_time = now
            with open(json_file, 'w') as f:
                json.dump({'last_run_time': last_run_time.isoformat()}, f)

        # Compute scheduled times between last_run_time and now
        scheduled_times = []
        current_time = last_run_time

        while True:
            current_time = next_scheduled_time(current_time)
            if current_time <= now:
                scheduled_times.append(current_time)
            else:
                break

        # For each missed cycle, perform the action
        for scheduled_time in scheduled_times:
            print(f'Missed scheduled time at {scheduled_time}, performing action now.')
            # Perform the action (print the time)
            print(f'Action performed for scheduled time: {scheduled_time}')
            if scheduled_time.hour == 9:
                pass
            if scheduled_time.hour == 21:
                # Restock the store
                store_data = load_store_data()
                for listing in store_data:
                    if listing['stock']['type'] == 'unlimited':
                        continue
                    for user in listing['stock']['users']:
                        listing['stock']['users'][user] += listing['stock']['restock-amount']
                        if listing['stock']['users'][user] >= listing['stock']['max']:
                            listing['stock']['users'][user] = listing['stock']['max']
                save_store_data(store_data)
                
        # Update last_run_time to the latest scheduled time
        if scheduled_times:
            last_run_time = scheduled_times[-1]
            # Write last_run_time to JSON file
            with open(json_file, 'w') as f:
                json.dump({'last_run_time': last_run_time.isoformat()}, f)

        # Now, set up an infinite loop to wait until the next scheduled time
        while True:
            next_time = next_scheduled_time(datetime.datetime.now())
            sleep_seconds = (next_time - datetime.datetime.now()).total_seconds()

            if sleep_seconds > 0:
                print(f'Next scheduled action in {sleep_seconds / 3600:.2f} hour(s) at {next_time}...')
                await asyncio.sleep(sleep_seconds)

            # Perform the action (print the time)
            print(f'Scheduled time: {next_time}, performing action.')
            # Update last_run_time
            last_run_time = next_time
            # Write last_run_time to JSON file
            with open(json_file, 'w') as f:
                json.dump({'last_run_time': last_run_time.isoformat()}, f)

    except asyncio.CancelledError:
        print('Scheduled actions are cancelled.')
        raise
    except Exception as e:
        print(f'An error occurred: {e}')

def previous_scheduled_time(now):
    today = now.date()
    nine_am_today = datetime.datetime.combine(today, datetime.time(hour=9))
    nine_pm_today = datetime.datetime.combine(today, datetime.time(hour=21))

    if now >= nine_pm_today:
        return nine_pm_today
    elif now >= nine_am_today:
        return nine_am_today
    else:
        # Go back to previous day's 9:00 PM
        yesterday = today - datetime.timedelta(days=1)
        nine_pm_yesterday = datetime.datetime.combine(yesterday, datetime.time(hour=21))
        return nine_pm_yesterday

def next_scheduled_time(now):
    today = now.date()
    nine_am_today = datetime.datetime.combine(today, datetime.time(hour=9))
    nine_pm_today = datetime.datetime.combine(today, datetime.time(hour=21))

    if now < nine_am_today:
        return nine_am_today
    elif now < nine_pm_today:
        return nine_pm_today
    else:
        # Go to next day's 9:00 AM
        tomorrow = today + datetime.timedelta(days=1)
        nine_am_tomorrow = datetime.datetime.combine(tomorrow, datetime.time(hour=9))
        return nine_am_tomorrow

command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True

intents = disnake.Intents.default()
intents.presences = False
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned,
    test_guilds=[guild_id],
    command_sync_flags=command_sync_flags,
    intents=intents
    )

@bot.event
async def on_ready():
    try:
        asyncio.run(scheduled_actions())
    except KeyboardInterrupt:
        pass
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
    await inter.response.defer(ephemeral=quiet)
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
        try:
            user = await bot.guilds[0].fetch_member(user_id)
            users += f'{user.nick or user.global_name or user.name}\n'
        except:
            user = await bot.fetch_user(user_id)
            users += f'{user.global_name or user.name}\n'
        ticket = str(user_data['tickets_earned'])
        tickets += f"{ticket} {emoji('ArcadeTicket')}\n"
    leaderboard_embed.add_field(name='Members', value=users)
    leaderboard_embed.add_field(name='Tickets Earned', value=tickets)
    await inter.edit_original_response(embed=leaderboard_embed)

@ticket.sub_command()
async def send(
    inter,
    user: disnake.Member,
    amount: int = commands.Param(gt=0),
    ):
    """
    Send ticket(s) to another user.

    Parameters
    ----------
    user: The user to send ticket(s) to.
    amount: The amount to send.
    """
    logger.info(f'{inter.author} used /ticket send(user: {user.name} amount: {amount})')
    user_data = ensure_user_data(user)
    if user_data[str(inter.author.id)]['tickets'] < amount:
        await inter.response.send_message(f"You can not send more tickets than you have.", ephemeral=True)
        logger.info(f'{inter.author} tried to send more tickets than they have ({amount})')
        return
    if user.bot:
        await inter.response.send_message(f"You can not send ticket(s) to bots.", ephemeral=True)
        logger.info(f'{inter.author} tried to send ticket(s) to a bot ({user.name})')
        return
    if user.id == inter.author.id:
        await inter.response.send_message(f"You can not send ticket(s) to yourself.", ephemeral=True)
        logger.info(f'{inter.author} tried to send ticket(s) to themself')
        return
    user_data[str(inter.author.id)]['tickets'] -= amount
    user_data[str(user.id)]['tickets'] += amount
    save_user_data(user_data)
    await inter.response.send_message(f"Sent {amount} {emoji('ArcadeTicket')} to {user.nick or user.global_name or user.name}.", ephemeral=True)
    logger.info(f'{inter.author} sent {amount} ticket(s) to {user.name}')
    dm = user.dm_channel or await user.create_dm()
    await dm.send(f"{inter.author.nick or inter.author.global_name or inter.author.name} ({inter.author.name}) sent you {amount} {emoji('ArcadeTicket')}!")
    return

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
                if 'data' in item:
                    if 'quantity' in item['data']:
                        if item['data']['quantity'] >= 2:
                            item_name += f' x{item['data']['quantity']}'
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
        await bot.guilds[0].get_channel(general_channel).send(random.choice(compliments))
        remove_inventory_item(inter.author, 'compliment-voucher')
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
            now = datetime.datetime.now()
            pix_found_date = f'{now.month}-{now.day}-{now.year}'
            pix_item = {
                'name': f"{pix_type_result.capitalize()} Pix#{str(random.randint(0, 9999)).rjust(4, '0')}",
                'emoji': 'Capsule',
                'image': image,
                'description': f"A creature known as a pix. This is a {pix_type_result} pix. It was found by {inter.author.display_name} on {pix_found_date}.",
                'tags': ['pix']
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
                if not store_result['name'] in inventory_item_names:
                    try:
                        add_inventory_item(inter.author, store_result)
                    except InventoryError as e:
                        await inter.response.send_message(f'Could not add item to inventory: {e}')
                        return
                    content = f"You got {emoji(store_result['emoji'])} {bold(store_result['name'])}!"
                    log_content = f"{store_result['name']}"
                    break
        remove_inventory_item(inter.author, 'capsule')
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

# Winterfest 2024 Code
event_data_file = 'event_data.json'
snowball_item = {
    'name': 'Snowball',
    'emoji': 'Snowball',
    'image': None,
    'description': 'A ball made of snow, perfect for throwing.',
    'data': {
        'quantity': 1
    },
    'tags': ['stackable'],
    'id': 'snowball'
}
hot_cocoa_item = {
    'name': 'Winterfest Hot Cocoa',
    'emoji': 'coffee',
    'image': None,
    'description': 'Drink this to get a bonus to your snowball throws.',
    'data': {
        'quantity': 1
    },
    'tags': ['stackable', 'hot-cocoa'],
    'id': 'hot-cocoa',
    'item_schema': 2
}

def load_event_data():
    if os.path.exists(event_data_file):
        with open(event_data_file) as file:
            return json.load(file)
    else:
        return {}

def save_event_data(event_data):
    with open(event_data_file, 'w') as file:
        json.dump(event_data, file, indent=4)

class winterfest2024PresentView(disnake.ui.View):
    def __init__(self, present: str):
        self.present = present
        super().__init__()

    @disnake.ui.button(label='Open', style=disnake.ButtonStyle.blurple, row=0)
    async def open(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        button.disabled = True
        user_data = ensure_user_data(inter.author)
        inventory = user_data[str(inter.author.id)]['inventory']
        inventory_item_names = []
        for inventory_item in inventory:
            inventory_item_names.append(inventory_item['name'])
        if not self.present in inventory_item_names:
            await inter.send(f"Could not find {emoji('gift')} {bold(self.present)} in your inventory.", ephemeral=True)
            logger.warning(f'{inter.author} tried to open non-existant present {self.present}')
            return
        event_data = load_event_data()
        if not 'present_openers' in event_data:
            event_data['present_openers'] = []
        if not inter.author.id in event_data['present_openers']:
            event_data['present_openers'].append(str(inter.author.id))
            save_event_data(event_data)
        if not 'snowman_parts_found' in event_data:
            event_data['snowman_parts_found'] = 0
        open_options = ['snowball', 'hot_cocoa']
        open_weights = [8, 1]
        if event_data['snowman_parts_found'] < 9:
            open_options.append('snowman_part')
            open_weights.append(1)
        result = random.choices(open_options, weights=open_weights, k=1)[0]
        snowball_quantity_str = ''
        if result == 'snowball':
            snowball_quantity = random.choices([1, 2, 3], weights=[3, 2, 1], k=1)[0]
            snowball_quantity_str = f' x{snowball_quantity}'
            item = snowball_item
            item['data']['quantity'] = snowball_quantity
            add_inventory_item(inter.author, item)
        elif result == 'hot_cocoa':
            item = hot_cocoa_item
            add_inventory_item(inter.author, item)
        elif result == 'snowman_part':
            snowman_part_list = ['', 'Snowball Base', 'Snowball Torso', 'Snowball Head', 'Left Arm', 'Right Arm', 'Coal Face', 'Coal Buttons', 'Carrot Nose', 'Top Hat']
            event_data['snowman_parts_found'] += 1
            save_event_data(event_data)
            found_part = snowman_part_list[event_data['snowman_parts_found']]
            item = {
                'name': f'Snowman Part: {found_part}',
                'emoji': 'Snowball'
            }
            snowman_embed = disnake.Embed(
                title='Winterfest Snowman',
                type='rich',
                description=f'{inter.author.display_name} added the {found_part}',
                color=disnake.Color.from_rgb(176, 224, 230), # Powder Blue
            )
            snowman_image_path = os.path.join(media_directory, 'Winterfest-2024', f'Snowman-{event_data['snowman_parts_found']}.png')
            with open(snowman_image_path, 'rb') as file:
                snowman_embed.set_image(file=disnake.File(file))
            await bot.guilds[0].get_channel(general_channel).send(embed=snowman_embed)
            if event_data['snowman_parts_found'] >= 9:
                await bot.guilds[0].get_channel(general_channel).send(f'The Winterfest Snowman has been finished! Everyone who has contributed by opening a present will receive a special commemorative role as well as a {emoji('rainbow')} {bold('Color-Role: Powder Blue')} item!')
                color_role_item = {
                    'name': 'Color Role: Powder Blue',
                    'emoji': 'rainbow',
                    'image': None,
                    'description': 'Activate it to get assigned a colored role.',
                    'data': {'color-role': 'b0e0e6'},
                    'tags': ['unique', 'color-role'],
                    'id': 'color-role-powder-blue',
                    'item_schema': 2
                }
                for opener_id in event_data['present_openers']:
                    # WF24 Snowman Builder Role: 1314989810590421002
                    member = disnake.utils.find(lambda m: str(m.id) == opener_id, bot.guilds[0].members)
                    snowman_role = disnake.utils.find(lambda r: r.id == 1314989810590421002, bot.guilds[0].roles)
                    member.add_roles(snowman_role)
                    add_inventory_item(member, color_role_item)
        remove_inventory_item(inter.author, 'winterfest-2024-present')
        await inter.send(f"You got {emoji(item['emoji'])} {bold(item['name'])}{snowball_quantity_str}!", ephemeral=True)
        logger.info(f'{inter.author} opened {self.present} and got {item['name']}')

class SnowballView(disnake.ui.View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label='Throw', style=disnake.ButtonStyle.blurple, row=0)
    async def send(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        button.disabled = True
        await inter.response.send_modal(
            title='Snowball',
            custom_id='snowball',
            components=[
                disnake.ui.TextInput(
                label='User',
                custom_id='user',
                style=disnake.TextInputStyle.short,
                placeholder='The user to throw the snowball at...',
                max_length=32
                )
            ]
        )

        try:
            modal_inter: disnake.ModalInteraction = await bot.wait_for(
                'modal_submit',
                check=lambda i: i.custom_id == 'snowball' and i.author.id == inter.author.id,
                timeout=300,
            )
        except asyncio.TimeoutError:
            return
        
        user = modal_inter.text_values['user']
        member = bot.guilds[0].get_member_named(user)
        if not member:
            await modal_inter.response.send_message(f"Could not find a member named {bold(user)}.", ephemeral=True)
            logger.debug(f'{inter.author} tried to throw a snowball at a non-existant member named {user}')
            self.stop()
            return
        event_data = load_event_data()
        cocoa_bonus = 0
        if not 'cocoa_bonuses' in event_data:
            event_data['cocoa_bonuses'] = {}
        if str(inter.author.id) in event_data['cocoa_bonuses']:
            cocoa_bonus = event_data['cocoa_bonuses'][str(inter.author.id)]
        roll_result = random.randrange(0, 20) + 1
        if roll_result == 20:
            throw_result = f'{inter.author.display_name} threw a snowball at {member.display_name} and got a perfect hit! They have earned some Hot Cocoa.'
            add_inventory_item(inter.author, hot_cocoa_item)
        elif roll_result == 1:
            throw_result = f'{inter.author.display_name} threw a snowball at {member.display_name}, but they caught it!'
            add_inventory_item(member, snowball_item)
        elif roll_result + cocoa_bonus >= 10:
            throw_result = f'{inter.author.display_name} threw a snowball at {member.display_name}, and hit.'
        else:
            throw_result = f'{inter.author.display_name} threw a snowball at {member.display_name}, but missed.'
        await bot.guilds[0].get_channel(general_channel).send(throw_result)
        remove_inventory_item(inter.author, 'snowball')
        await modal_inter.response.send_message(f'Threw snowball at {bold(member.display_name)}.', ephemeral=True)
        logger.info(f'{throw_result}')
        self.stop()

class CocoaView(disnake.ui.View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label='Drink', style=disnake.ButtonStyle.blurple, row=0)
    async def drink(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        button.disabled = True
        event_data = load_event_data()
        if not 'cocoa_bonuses' in event_data:
            event_data['cocoa_bonuses'] = {}
        if not str(inter.author.id) in event_data['cocoa_bonuses']:
            event_data['cocoa_bonuses'][str(inter.author.id)] = 0
        event_data['cocoa_bonuses'][str(inter.author.id)] += 1
        save_event_data(event_data)
        remove_inventory_item(inter.author, 'hot-cocoa')
        await inter.send(f"You drank a hot cocoa, your bonus to snowball throws is now {event_data['cocoa_bonuses'][str(inter.author.id)]}.", ephemeral=True)
        logger.info(f'{inter.author.display_name} drank a hot cocoa, their snowball throw bonus is now {event_data['cocoa_bonuses'][str(inter.author.id)]}.')
        self.stop()

@bot.slash_command()
async def item(inter):
    pass

@item.sub_command()
async def show(inter, item: str = commands.Param(autocomplete=autocomplete_items), quiet: bool = True):
    """
    Display the details of an item.

    Parameters
    ----------
    item: The item to inspect.
    """
    logger.info(f'{inter.author} used /item show(item: {item}, quiet: {quiet})')
    user_data = ensure_user_data(inter.author)
    inventory = user_data[str(inter.author.id)]['inventory']
    inventory_item = next((search_item for search_item in inventory if search_item['name'] == item), None)
    if not inventory_item:
        await inter.response.send_message(f"Could not find {bold(item)} in your inventory.", ephemeral=True)
        return
    item_show_embed_title = f"{emoji(inventory_item['emoji'])} {inventory_item['name']}"
    if 'data' in inventory_item:
        if 'quantity' in inventory_item['data']:
            if inventory_item['data']['quantity'] >= 2:
                item_show_embed_title += f' x{inventory_item['data']['quantity']}'
    item_show_embed = disnake.Embed(
        title=item_show_embed_title,
        type='rich',
        description=inventory_item['description'],
        color=main_color,
    )
    if inventory_item['image']:
        filepath = os.path.join(media_directory, inventory_item['image'])
        with open(filepath, 'rb') as file:
            item_show_embed.set_image(file=disnake.File(file))
    tags = ', '.join(inventory_item['tags'])
    item_show_embed.set_footer(text=f"tags: {tags or 'None'}")
    view = None
    if 'compliment-voucher' in inventory_item['tags']:
        view = ComplimentVoucherView()
    elif 'capsule' in inventory_item['tags']:
        view = CapsuleView(item)
    elif 'color-role' in inventory_item['tags']:
        view = ColorRoleView(inventory_item['tags']['color-role'])
    elif inventory_item[id] == 'winterfest-2024-present':
        view = winterfest2024PresentView(item)
    elif inventory_item[id] == 'snowball':
        view = SnowballView()
    elif inventory_item[id] == 'hot-cocoa':
        view = CocoaView()
    if view:
        await inter.response.send_message(embed=item_show_embed, view=view, ephemeral=True)
    else:
        await inter.response.send_message(embed=item_show_embed, ephemeral=quiet)

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
        logger.warning(f"Could not find {item} in {inter.author}'s inventory")
        return
    if user.bot:
        await inter.response.send_message(f"You can not send items to bots.", ephemeral=True)
        logger.warning(f'{inter.author} tried to send an item to a bot ({user.name})')
        return
    if user.id == inter.author.id:
        await inter.response.send_message(f"You can not send items to yourself.", ephemeral=True)
        logger.warning(f'{inter.author} tried to send an item to themself')
        return
    try:
        add_inventory_item(user, inventory_item)
    except InventoryError as e:
        await inter.response.send_message(f'Could not send item: {e}')
        return
    remove_inventory_item(inter.author, inventory_item['id'])
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
        listing_name = listing['item']['name']
        listing_emoji = listing['item']['emoji']
        listing_description = listing['item']['description']
        if 'store-override' in listing:
            if 'name' in listing['store-override']:
                listing_name = listing['store-override']['name']
            if 'emoji' in listing['store-override']:
                listing_emoji = listing['store-override']['emoji']
            if 'description' in listing['store-override']:
                listing_description = listing['store-override']['description']
        store_display_embed_name = f"{emoji(listing_emoji)} {bold(listing_name)}"
        store_display_embed_value = f"{listing_description}\nPrice: {listing['price']} {emoji('ArcadeTicket')}"
        if listing['stock']['type'] != 'unlimited':
            if str(inter.author.id) in listing['stock']['users']:
                listing_stock = listing['stock']['users'][str(inter.author.id)]
            else:
                listing_stock = listing['stock']['initial']
            store_display_embed_value += f' | Stock: {listing_stock}'
        store_display_embed.add_field(
            name = store_display_embed_name,
            value = store_display_embed_value,
            inline = False
        )
    store_display_embed.set_footer(text="Use '/store buy {item}' to purchase.\nItems and prices subject to change.")
    await inter.response.send_message(embed=store_display_embed, ephemeral=True)

async def autocomplete_store_items(inter, string: str) -> List[str]:
    store_data = load_store_data()
    item_names = []
    for listing in store_data:
        listing_name = listing['item']['name']
        if 'store-override' in listing:
            if 'name' in listing['store-override']:
                listing_name = listing['store-override']['name']
        item_names.append(listing_name)
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
    store_data = load_store_data()
    for index, listing in enumerate(store_data):
        listing_name = listing['item']['name']
        if 'store-override' in listing:
            if 'name' in listing['store-override']:
                listing_name = listing['store-override']['name']
        if listing_name == item:
            if not listing['stock']['type'] == 'unlimited':
                if str(inter.author.id) in listing['stock']['users']:
                    listing_stock = listing['stock']['users'][str(inter.author.id)]
                else:
                    listing_stock = listing['stock']['initial']
                if listing_stock <= 0:
                    await inter.response.send_message(f"{emoji(listing['item']['emoji'])} {bold(listing['item']['name'])} is out of stock.", ephemeral=True)
                    return
            if not user_data[str(inter.author.id)]['tickets'] >= listing['price']:
                await inter.response.send_message(f"You don't have enough tickets for {emoji(listing['item']['emoji'])} {bold(listing['item']['name'])}.", ephemeral=True)
                return
            try:
                add_inventory_item(inter.author, listing['item'])
            except InventoryError as e:
                await inter.response.send_message(f'Could not add item to inventory: {e}')
                return
            user_data[str(inter.author.id)]['tickets'] -= listing['price']
            save_user_data(user_data)
            if listing['stock']['type'] != 'unlimited':
                if str(inter.author.id) in listing['stock']['users']:
                    store_data[index]['stock']['users'][str(inter.author.id)] -= 1
                else:
                    store_data[index]['stock']['users'][str(inter.author.id)] = listing['stock']['initial'] - 1
                save_store_data(store_data)
            await inter.response.send_message(f"You purchased {emoji(listing['item']['emoji'])} {bold(listing['item']['name'])}! Your new balance is {user_data[str(inter.author.id)]['tickets']} {emoji('ArcadeTicket')}.", ephemeral=True)
            return
    await inter.response.send_message(f"Could not find {bold(item)} in the store.", ephemeral=True)

@bot.slash_command()
async def roll(inter, dice_expression: str):
    """
    Resolves dice expressions such as '2d20kh + 4d4x + 6'.

    Parameters
    ----------
    dice expression: The dice you wish to roll, and modifiers to apply to them.
    """
    logger.info(f'{inter.author} used /roll(dice_expression: {dice_expression})')
    result = dice_express.eval_dice_express(dice_expression)
    await inter.response.send_message(f'{result}')

bot.run(bot_token)