import planets

def nameValues():
    for i in range(len(planets.planets)):
        print(planets.planets[i].name)

def atmosphereCompTotalValues():
    n=0
    for x in planets.planets:
        for y in range(len(x.atmosphereComp)):
            n+=x.atmosphereComp[y][1]
        print(x.name,": ",n)
        n=0
atmosphereCompTotalValues()