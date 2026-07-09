# Toteutusdokumentti

## Ohjelman yleisrakenne

Ohjelma on Pythonilla toteutettu polunetsintasovellus oktili-ruudukoille. Se tukee Moving AI -muotoisia `.map`-karttatiedostoja ja `.scen`-skenaariotiedostoja.

- sovellus alkaa cli.py tiedostosta jossa konsolin sisäinen käyttäliittymä
- grid lukee karttatiedostot ja varmistaa että ne okei. 
- A*/JPS algoritmejä joita voidaan käyttää reitin etsimiseen.
- benchmark vertailee tuloksia. (tekoälyllä kun ope antoi luvan)
- visualize visualisoi tulokset. (tekoälyllä kun ope antoi luvan) 
- results listaa tärkeät määreet
- scenarios lukee .scen tiedostot

## Saavutetut aika- ja tilavaativuudet

A* ja JPS sama. 
worst case scenario O(E log V)
best case scenario O(V)

aikavertailun löydät [benchmark](./benchmarktuloksia.md)

## Tyon mahdolliset puutteet ja parannusehdotukset

- optimoida JPS:n `jump`-funktion toistuvia tarkistuksia esimerkiksi esilasketuilla kulkukelpoisuusrakenteilla
- lisätä graafinen käyttöliittymä, jossa alku- ja maalipisteen voisi valita kartalta


## lähteet

<https://users.cecs.anu.edu.au/~dharabor/data/papers/harabor-grastien-aaai11.pdf>

<https://zerowidth.com/2013/a-visual-explanation-of-jump-point-search/>

<https://harablog.wordpress.com/2011/09/07/jump-point-search/>

<https://en.wikipedia.org/wiki/A*_search_algorithm>