import json

data = json.load(open('atp_data.json'))
players = [p['name'] for p in data['players']]

madrid = [
    'Adam Walton','Adolfo Daniel Vallejo','Adrian Mannarino',
    'Alejandro Davidovich Fokina','Alejandro Tabilo','Aleksandar Kovacevic',
    'Aleksandar Vukic','Aleksandr Shevchenko','Alex de Minaur','Alex Michelsen',
    'Alexander Blockx','Alexander Bublik','Alexander Zverev','Alexandre Muller',
    'Alexei Popyrin','Andrea Pellegrino','Andrey Rublev','Arthur Fils',
    'Arthur Gea','Arthur Rinderknech','Ben Shelton','Brandon Nakashima',
    'Cameron Norrie','Carlos Alcaraz','Casper Ruud','Christopher Oconnell',
    'Corentin Moutet','Daniil Medvedev','Fabian Marozsan','Felix Auger-Aliassime',
    'Flavio Cobolli','Francisco Cerundolo','Francisco Comesana','Gabriel Diallo',
    'Holger Rune','Hubert Hurkacz','Jakub Mensik','Jan Lennard Struff',
    'Jannik Sinner','Jaume Munar','Jiri Lehecka','Joao Fonseca',
    'Jordan Thompson','Karen Khachanov','Learner Tien','Lorenzo Musetti',
    'Lorenzo Sonego','Luciano Darderi','Mariano Navone','Mattia Bellucci',
    'Novak Djokovic','Nuno Borges','Reilly Opelka','Sebastian Baez',
    'Stefanos Tsitsipas','Tallon Griekspoor','Taylor Fritz',
    'Tomas Martin Etcheverry','Tommy Paul','Valentin Vacherot','Zizou Bergs'
]

missing = [p for p in madrid if p not in players]
found = [p for p in madrid if p in players]

print("Found in database: " + str(len(found)))
print("Missing from database: " + str(len(missing)))
print()
if missing:
    print("MISSING PLAYERS:")
    for m in missing:
        print("  - " + m)
else:
    print("All Madrid players are in the database!")