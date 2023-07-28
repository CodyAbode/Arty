last = -2
for i in range(1, 21):
    exp = i * 2 + last
    last = exp
    print(f'- Level {i}: {exp}')