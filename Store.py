import json

# item schema 1
{
    'name': 'str',
    'emoji': 'str',
    'image': 'str' or None,
    'description': 'str',
    'tags': {},
}

# item schema 2
{
    'name': 'str',
    'emoji': 'str',
    'image': 'str' or None,
    'description': 'str',
    'data': {},
    'tags': [],
    'id': 'str',
    'created': 'strftime',
    'modified': 'strftime',
    'item_schema': 2,
}

# tags
# unique: can only have one in inventory
# stackable: has quantity data, can not be unique
# color-role: has color data, can set cosmetic user role
# gift-card: redeemable gift card
# pix: a digital creature with pix data
# {rarity}: common (white), uncommon (green), rare (blue), epic (purple), legendary (orange)

# store schema 1
{
    'item': {},
    'price': 0,
}

# store schema 2
{
    'item': {},
    'price': 0,
    'discount-price': None or 0,
    'store-override': {},
    'stock': {},
}

# stock
{
    'type': 'unlimited' or 'user' or 'server',
    # fields below not need for unlimited type
    'initial': 0,
    'max': 0,
    'users': {}, # only for user type
    'server': 0, # only for server type
    'restock': None or 'daily' or 'weekly' or 'monthly',
    'restock-amount': 0
}

store_data = [
    {
        'item': {
            'name': 'Winterfest Present',
            'emoji': 'gift',
            'image': None,
            'description': 'Open it up for a random festive surprise!',
            'data': {
                'quantity': 1
            },
            'tags': ['stackable'],
            'id': 'winterfest-2024-present',
            'item_schema': 2
        },
        'price': 0,
        'store-override': {
            'name': 'Daily Winterfest Present'
        },
        'stock': {
            'type': 'user',
            'initial': 1,
            'max': 1,
            'users': {},
            'restock': 'daily',
            'restock-amount': 1
        }
    },
    {
        'item': {
            'name': 'Winterfest Present',
            'emoji': 'gift',
            'image': None,
            'description': 'Open it up for a random festive surprise!',
            'data': {
                'quantity': 1
            },
            'tags': ['stackable'],
            'id': 'winterfest-2024-present',
            'item_schema': 2
        },
        'price': 1,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Arty Compliment Voucher',
            'emoji': 'blue_heart',
            'image': 'ArtyTicketSmall.png',
            'description': 'Redeem to get a compliment from Arty for yourself or another member.',
            'data': {
                'quantity': 1
            },
            'tags': ['stackable', 'compliment-voucher'],
            'id': 'compliment-voucher',
            'item_schema': 2
        },
        'price': 3,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Capsule',
            'emoji': 'Capsule',
            'image': 'Capsule.png',
            'description': 'Open it up for a random surprise!',
            'data': {
                'quantity': 1
            },
            'tags': ['stackable', 'capsule'],
            'id': 'capsule',
            'item_schema': 2
        },
        'price': 10,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Color Role: Brown',
            'emoji': 'brown_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'data': {'color-role': 'c1694f'},
            'tags': ['unique', 'color-role'],
            'id': 'color-role-brown',
            'item_schema': 2
        },
        'price': 10,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Color Role: Orange',
            'emoji': 'orange_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'data': {'color-role': 'f4900c'},
            'tags': ['unique', 'color-role'],
            'id': 'color-role-orange',
            'item_schema': 2
        },
        'price': 10,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Color Role: Yellow',
            'emoji': 'yellow_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'data': {'color-role': 'fdcb59'},
            'tags': ['unique', 'color-role'],
            'id': 'color-role-yellow',
            'item_schema': 2
        },
        'price': 10,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Color Role: Blue',
            'emoji': 'blue_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'data': {'color-role': '55acee'},
            'tags': ['unique', 'color-role'],
            'id': 'color-role-blue',
            'item_schema': 2
        },
        'price': 20,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Color Role: Green',
            'emoji': 'green_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'data': {'color-role': '77b256'},
            'tags': ['unique', 'color-role'],
            'id': 'color-role-green',
            'item_schema': 2
            
        },
        'price': 20,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Color Role: Purple',
            'emoji': 'purple_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'data': {'color-role': 'ab8ed8'},
            'tags': ['unique', 'color-role'],
            'id': 'color-role-purple',
            'item_schema': 2
        },
        'price': 20,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Color Role: Red',
            'emoji': 'red_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'data': {'color-role': 'dd2e44'},
            'tags': ['unique', 'color-role'],
            'id': 'color-role-red',
            'item_schema': 2
            
        },
        'price': 20,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Color Role: Black',
            'emoji': 'black_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'data': {'color-role': '31373d'},
            'tags': ['unique', 'color-role'],
            'id': 'color-role-black',
            'item_schema': 2
        },
        'price': 40,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Color Role: White',
            'emoji': 'white_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'data': {'color-role': 'e7e8e8'},
            'tags': ['unique', 'color-role'],
            'id': 'color-role-white',
            'item_schema': 2
        },
        'price': 40,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Color Role: Custom',
            'emoji': 'rainbow',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'data': {'color-role': 'custom'},
            'tags': ['unique', 'color-role'],
            'id': 'color-role-custom',
            'item_schema': 2
        },
        'price': 80,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Steam Gift Card ($5)',
            'emoji': 'credit_card',
            'image': 'SteamGiftCard.png',
            'description': 'Redeemable for $5 on Steam!',
            'tags': ['unique', 'gift-card'],
            'id': 'steam-gc',
            'item_schema': 2
        },
        'price': 250,
        'stock': {
            'type': 'unlimited'
        }
    },
    {
        'item': {
            'name': 'Discord Nitro (1 Month)',
            'emoji': 'credit_card',
            'image': 'DiscordNitro.png',
            'description': 'Redeemable for one month of Discord Nitro!',
            'tags': ['unique', 'gift-card'],
            'id': 'nitro-gc',
            'item_schema': 2
        },
        'price': 500,
        'stock': {
            'type': 'unlimited'
        }
    },
]

with open('store_data.json', 'w') as file:
    json.dump(store_data, file, indent=4)