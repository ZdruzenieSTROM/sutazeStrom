from tkinter import Tk
import random

r = Tk()
r.withdraw()
r.clipboard_clear()

CSV_FIELDS = [
    'tim',
    'skola',
    'ico',
    'pocet_clenov',
    'kontakt_meno',
    'kontakt_email',
    'kontakt_tel',
    'ucastnik1_meno',
    'ucastnik1_priezvisko',
    'ucastnik1_rocnik',
    'ucastnik1_email',
    'ucastnik1_a1',
    'ucastnik1_a2',
    'ucastnik1_a3',
    'ucastnik2_meno',
    'ucastnik2_priezvisko',
    'ucastnik2_rocnik',
    'ucastnik2_email',
    'ucastnik2_a1',
    'ucastnik2_a2',
    'ucastnik2_a3',
    'ucastnik3_meno',
    'ucastnik3_priezvisko',
    'ucastnik3_rocnik',
    'ucastnik3_email',
    'ucastnik3_a1',
    'ucastnik3_a2',
    'ucastnik3_a3',
    'ucastnik4_meno',
    'ucastnik4_priezvisko',
    'ucastnik4_rocnik',
    'ucastnik4_email',
    'ucastnik4_a1',
    'ucastnik4_a2',
    'ucastnik4_a3',
    'cislo_timu',
]

ROCNIKY = [
    'prvý',
    'druhý',
    'tretí',
    'štvrtý',
    'piaty',
    'šiesty',
    'príma',
    'siedmy',
    'sekunda',
    'ôsmy',
    'tercia',
    'deviaty',
    'kvarta',
]

dataset = ''
for field in CSV_FIELDS:
    dataset += field + ';'

dataset = dataset[:-1] + '\n'
for i in range(900):
    for field in CSV_FIELDS:
        if field == 'pocet_clenov':
            dataset += '4'
        elif 'rocnik' in field:
            dataset += random.choice(ROCNIKY)
        else:
            for j in range(5):
                dataset += random.choice('asdfghjklqwertyuiopzxcvbnm')

        dataset += ';'
    dataset = dataset[:-1] + '\n'

dataset = dataset[:-1]

r.clipboard_append(dataset)
r.update()
r.destroy()
