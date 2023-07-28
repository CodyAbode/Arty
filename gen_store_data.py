import json

store_data = [
    {
        'item': {
            'name': 'Arty Compliment Voucher',
            'emoji': 'blue_heart',
            'image': 'ArtyTicketSmall.png',
            'description': 'Redeem to get a compliment from Arty for yourself or another member.',
            'tags': {'unique': True, 'compliment-voucher': True},
        },
        'price': 3
    },
    {
        'item': {
            'name': 'Capsule',
            'emoji': 'Capsule',
            'image': 'Capsule.png',
            'description': 'Open it up for a random surprise!',
            'tags': {'capsule': True}
        },
        'price': 10
    },
    {
        'item': {
            'name': 'Color Role: Brown',
            'emoji': 'brown_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'tags': {'unique': True, 'color-role': 'c1694f'}
        },
        'price': 10
    },
    {
        'item': {
            'name': 'Color Role: Orange',
            'emoji': 'orange_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'tags': {'unique': True, 'color-role': 'f4900c'}
        },
        'price': 10
    },
    {
        'item': {
            'name': 'Color Role: Yellow',
            'emoji': 'yellow_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'tags': {'unique': True, 'color-role': 'fdcb59'}
        },
        'price': 10
    },
    {
        'item': {
            'name': 'Color Role: Blue',
            'emoji': 'blue_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'tags': {'unique': True, 'color-role': '55acee'}
        },
        'price': 20
    },
    {
        'item': {
            'name': 'Color Role: Green',
            'emoji': 'green_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'tags': {'unique': True, 'color-role': '77b256'}
        },
        'price': 20
    },
    {
        'item': {
            'name': 'Color Role: Purple',
            'emoji': 'purple_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'tags': {'unique': True, 'color-role': 'ab8ed8'}
        },
        'price': 20
    },
    {
        'item': {
            'name': 'Color Role: Red',
            'emoji': 'red_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'tags': {'unique': True, 'color-role': 'dd2e44'}
        },
        'price': 20
    },
    {
        'item': {
            'name': 'Color Role: Black',
            'emoji': 'black_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'tags': {'unique': True, 'color-role': '31373d'}
        },
        'price': 40
    },
    {
        'item': {
            'name': 'Color Role: White',
            'emoji': 'white_circle',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'tags': {'unique': True, 'color-role': 'e7e8e8'}
        },
        'price': 40
    },
    {
        'item': {
            'name': 'Color Role: Custom',
            'emoji': 'rainbow',
            'image': None,
            'description': 'Activate it to get assigned a colored role.',
            'tags': {'unique': True, 'color-role': 'custom'}
        },
        'price': 80
    },
    {
        'item': {
            'name': 'Steam Gift Card ($5)',
            'emoji': 'credit_card',
            'image': 'SteamGiftCard.png',
            'description': 'Redeemable for $5 on Steam!',
            'tags': {'unique': True, 'gift-card': True}
        },
        'price': 250
    },
    {
        'item': {
            'name': 'Discord Nitro (1 Month)',
            'emoji': 'credit_card',
            'image': 'DiscordNitro.png',
            'description': 'Redeemable for one month of Discord Nitro!',
            'tags': {'unique': True, 'gift-card': True}
        },
        'price': 500
    },
]

with open('store_data.json', 'w') as file:
    json.dump(store_data, file, indent=4)