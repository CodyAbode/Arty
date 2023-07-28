import json

pix_data = {
    'levels': [0, 4, 10, 18, 28, 40, 54, 70, 88, 108, 130, 154, 180, 208, 238, 270, 304, 340, 378, 418],
    'default': {
        'nickname': '',
        'level': 1,
        'experience': 0,
        'max_health': 4,
        'health': 4,
        'thirst': 3,
        'hunger': 3,
        'strength': 1,
        'agility': 1,
        'intelligence': 1,
        'max_stamina': 4,
        'stamina': 4,
    },
    'growth_values': {
        'basic': {
            'health': 0.8,
            'strength': 0.8,
            'agility': 0.8,
            'intelligence': 0.8,
            'stamina': 0.8,
        },
        'mask': {
            'health': 0.8,
            'strength': 1.0,
            'agility': 0.8,
            'intelligence': 0.8,
            'stamina': 0.8,
        },
        'furry': {
            'health': 0.8,
            'strength': 0.8,
            'agility': 1.0,
            'intelligence': 0.8,
            'stamina': 1.0,
        },
        'grated': {
            'health': 1.0,
            'strength': 1.0,
            'agility': 0.8,
            'intelligence': 1.0,
            'stamina': 0.8,
        },
        'combined': {
            'health': 0.8,
            'strength': 1.0,
            'agility': 1.0,
            'intelligence': 1.0,
            'stamina': 1.0,
        },
        'linear': {
            'health': 1.0,
            'strength': 0.8,
            'agility': 1.4,
            'intelligence': 0.8,
            'stamina': 1.0,
        },
        'wild': {
            'health': 1.2,
            'strength': 1.0,
            'agility': 1.0,
            'intelligence': 0.8,
            'stamina': 1.2,
        },
        'thorny': {
            'health': 1.4,
            'strength': 1.0,
            'agility': 1.0,
            'intelligence': 1.0,
            'stamina': 1.0,
        },
        'poisonous': {
            'health': 0.8,
            'strength': 1.4,
            'agility': 1.0,
            'intelligence': 1.0,
            'stamina': 1.4,
        },
        'mystical': {
            'health': 1.0,
            'strength': 1.0,
            'agility': 1.2,
            'intelligence': 1.6,
            'stamina': 1.0,
        },
        'elemental': {
            'health': 1.2,
            'strength': 1.4,
            'agility': 1.0,
            'intelligence': 1.0,
            'stamina': 1.4,
        },
        'ancient': {
            'health': 1.4,
            'strength': 1.2,
            'agility': 1.2,
            'intelligence': 1.2,
            'stamina': 1.2,
        },
    },
    'mood_matrix': [],
}

# thirst, hunger, social
pix_data['mood_matrix'][0][0][0] = 'They are despressed.'

with open('pix_data.json', 'w') as file:
    json.dump(pix_data, file, indent=4)