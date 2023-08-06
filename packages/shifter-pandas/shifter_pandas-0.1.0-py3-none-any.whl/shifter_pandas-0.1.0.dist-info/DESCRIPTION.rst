# Convert some data into Panda DataFrames

## British Petroleum (BP)

It parse sheet like `Primary Energy Consumption` (not like `Primary Energy - Cons by fuel`).

Open: http://www.bp.com/statisticalreview
or https://www.bp.com/en/global/corporate/energy-economics/statistical-review-of-world-energy.html

Download `Statistical Review of World Energy – all data`.

Use:

... see it on GitHub

## Swiss Office Federal of Statistics (OFS)

From https://www.bfs.admin.ch/bfs/fr/home/services/recherche/stat-tab-donnees-interactives.html
create a stat table.

Click on `À propos du tableau`

Click on `Rendez ce tableau disponible dans votre application`

Use:

... see it on GitHub

And replace `<URL>` and `<Requête Json>` with the content of the fields of the OFS web page.

### Interesting sources

- [Parc de motocycles par caractéristiques techniques et émissions](https://www.pxweb.bfs.admin.ch/pxweb/fr/px-x-1103020100_165/-/px-x-1103020100_165.px/)
- [Bilan démographique selon l'âge et le canton](https://www.pxweb.bfs.admin.ch/pxweb/fr/px-x-0102020000_104/-/px-x-0102020000_104.px/)

## Our World in Data

Select a publication.

Click `Download`.

Click `Full data (CSV)`.

Use:

... see it on GitHub

### Interesting sources

- [GDP, 1820 to 2018](https://ourworldindata.org/grapher/gdp-world-regions-stacked-area)
- [Population, 1800 to 2021](https://ourworldindata.org/grapher/population-since-1800)

## World Bank

Open https://data.worldbank.org/

Find a chart

In `Download` click `CSV`

Use:

... see it on GitHub

### Interesting sources

- [GDP (current US$)](https://data.worldbank.org/indicator/NY.GDP.MKTP.CD)
- [GDP (constant 2015 US$)](https://data.worldbank.org/indicator/NY.GDP.MKTP.KD)

## Wikidata

By providing the `wikidata_*` parameters, you can ass some data from WikiData.

Careful, the WikiData is relatively slow then the first time you run it il will be slow.
We use a cache to make it fast the next times.

You can also get the country list with population and ISO 2 code with:

... see it on GitHub


