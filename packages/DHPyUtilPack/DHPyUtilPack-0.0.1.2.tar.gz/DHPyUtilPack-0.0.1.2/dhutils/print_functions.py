def progress_show(current, total, gap=0.0001):
    number = int(total * gap)
    if current != 0 and number != 0:
        if current % number == 0:
            print(round(100 * current / total, 2), ' % ')
