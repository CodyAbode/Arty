import re
import random

def eval_roll_express(roll_express: str):
    rolls = []
    split_roll = roll_express.split('d')
    if split_roll[0]:
        dice_count = int(split_roll[0])
        if dice_count == '0':
            return 0
    else:
        dice_count = 1
    dice_faces = int(re.search(r'\d*', split_roll[1]).group())

    roll_count = 0
    while roll_count < (dice_count):
        roll_result = random.randrange(0, dice_faces) + 1
        rolls.append(roll_result)
        if roll_express.endswith('x'):
            if roll_result == dice_faces:
                roll_count -= 1
        roll_count += 1
    print(rolls)

    if roll_express.endswith('kh'):
        return max(rolls)
    elif roll_express.endswith('kl'):
        return min(rolls)
    else:
        return sum(rolls)

def eval_dice_express(dice_express: str):
    dice_express = (''.join(dice_express.split())).lower()
    roll_re = r'\d*d\d+(?:kh|kl|x)?'
    valid_chars_re = r'(\d*d\d+(?:kh|kl|x)?|[+\-*/()]|\d)*'

    if not re.fullmatch(valid_chars_re, dice_express):
        print('Invalid dice expression')
        return None

    while roll_re_match := re.search(roll_re, dice_express):
        roll_express = roll_re_match.group()
        dice_express = \
            re.sub(roll_re, str(eval_roll_express(roll_express)), dice_express, 1)
    
    print(dice_express)
    dice_express_result = eval(dice_express)
    return dice_express_result

def main():
    dice_express_input = input('dice expression> ').lower()
    dice_express_result = eval_dice_express(dice_express_input)
    print(dice_express_result)

if __name__ == "__main__":
    main()