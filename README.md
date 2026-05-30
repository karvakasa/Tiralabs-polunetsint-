# Verkot ja polunetsintä

Python-projekti, joka etsii lyhimmän reitin oktili-ruudukoissa A*-algoritmillä ja JPS algoritmillä.

## Asennus ja testien komentoja

Asenna riippuvuudet:

```bash
poetry install
```

Aja testit:

```bash
poetry run invoke test
```

Tiedoston .pylintrc määrittelemät tarkistukset voi suorittaa komennolla:

```bash
poetry run invoke lint
```

Aja coverage ja luo raportti:

```bash
poetry run invoke coverage
```
## Käyttöohje sovellukseen

Aja reitti pienella kartalla:

```bash
poetry run invoke start
```

Voit käyttaa myös interactive komentoa:

```bash
poetry run invoke interactive
```

## komentorivi CLI

käyttöliittymä kysyy kartan, reitin lahteen, ASCII-tulosteen ja HTML-tiedoston polun. Oletusarvot kayttavat pienta testikarttaa, joten voit painaa `enter` kaikessa.

komennon 
    ```bash
    poetry run invoke interactive
    ```
jälkeen käyttöliittymä pyytää sinulta seuraavia asioita:
    
    1. Mitä karttaa käytetään: (oletus pieni kartta)
        1.1 voit myös ladata lisää karttoja alempana olevasta linkistä ja tallentaa .map ja .scen tidostot maps folderiin.
    2. laitatko manuaalisesti lähtö/maali pisteet vai käytätkö scenaario tiedoston lähtö/maali pisteitä: (oletus on manuaalinen laitto)
    3. koordinaattien laitto alkupisteelle: (oletuksena 1,1)
    4. koordinaattien laitto maalipisteelle: (oletus 7,4)
    5. näytetäänkö ASCII visualisointi (oletus kyllä)

##  ASCII-visualisointi:

- `S` = lähtö
- `E` = maali
- `*` = lopullinen polku
- `+` = vierailtu solmu
- `#` = estetty solmu
- `.` = käymätön solmu

## Kartat

Sovellus tukee `.map` ja `.scen` -tiedostoja. (`https://www.movingai.com/benchmarks/grids.html`)

## Liikkumisen hinta algoritmissä
Suorat liikkeet maksavat `1`, poikittaiset liikkeet maksavat `sqrt(2)` ja poikittaiset liikkeet eivät voi leikata nurkkia estettyjen solmujen läpi.
