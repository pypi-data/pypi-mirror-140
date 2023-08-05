import random

names = [
    "Reveille",
    "AI Constructs and Cyborgs First!",
    "Flawless Cowboy",
    "Reunion Tour",
    "The Truth and Reconciliation",
    "Into the Belly of the Beast",
    "Shut Up and Get Behind me... Sir",
    "The Silent Cartographer",
    "It's Quiet...",
    "Shafted",
    "I Would Have Been Your Daddy...",
    "Rolling Thunder",
    "If I had a Super Weapon...",
    "Well Enough Alone",
    "The Flood",
    "343 Guilty Spark",
    "The Library",
    "Wait, It Gets Worse!",
    "But I Don't Want to Ride the Elevator!",
    "Fourth Floor: Tools, Guns, Keys to Super Weapons",
    "The Gun Point at the Head of the Universe",
    "Breaking Stuff to Look Tough",
    "The Tunnels Below",
    "Final Run",
    "Under New Management",
    "Upstairs, Downstairs",
    "The Captain",
    "...And the Horse You Rode in on",
    "Light Fuse, Run Away",
    "Warning: Hitchhikers May be Escaping Convicts"
]

def get_level():
    return names[random.randrange(len(names))]