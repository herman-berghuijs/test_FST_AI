# Verbetersuggesties (niet uitgevoerd)

1. Voeg een variabelenlijst met eenheden toe, zodat straling, water en biomassa
   zonder terugzoeken in de FST-bron te interpreteren zijn.
2. Zet vaste getallen in GLA, PENMAN en het hoofdprogramma om naar benoemde
   parameters; behoud bij die latere wijziging de bestaande standaardwaarden.
3. Groepeer parameters per gewas, bodem, beheer en locatie in een configuratiebestand.
4. Splits `TSUMAN` in een drempel voor bladveroudering en een voor het stoppen
   van wortelgroei; nu hebben beide processen dezelfde parameter.
5. Begrens worteldiepte op `ROOTDM`; de huidige dagstap schiet door tot 1,204 m.
6. Gebruik een expliciete opkomstvlag in plaats van `LAI == 0` en de
   `EMERG`-constructie; beoordeel daarbij de overschrijfvolgorde van de GLA-IF-regels.
7. Maak de EXPLOR-aanname configureerbaar: nieuw beworteld bodemvolume
   bevat nu altijd water op veldcapaciteit.
8. Voeg controles op de water- en drogestofbalans toe.
9. Verzamel referentieruns zonder beregening en voor andere jaren om de
   droogtelogica onafhankelijk te valideren.
10. Voeg een bron voor de tarweparameters toe; de huidige header verwijst
    naar een publicatie over aardappel.
11. Documenteer de CABO-kwaliteitsvlaggen met een gecontroleerde bron:
    dit weerbestand bevat 24 `-999`-regels die geen meetdagen zijn.
12. Verwijder ongebruikte Fortran-berekeningen: `WAFC` in EVAPTR en `WC`
    in DRUNIR hebben geen effect en zijn in deze Python-port weggelaten.
13. Beschrijf de uitvoerconventie voor `TRANRF` bij nul potentiële transpiratie:
    door `NOTNUL` is die waarde 0, ook in een beregende run.
