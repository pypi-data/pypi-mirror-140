import planets

def nameValues():
    for i in range(len(planets.planets)):
        print(planets.planets[i].name)

def atmosphereCompTotalValues():
    n=0
    for x in planets.planets:
        for y in x.atmosphereComp.values():
            n+=y
        print(x.name,": ",n)
        n=0