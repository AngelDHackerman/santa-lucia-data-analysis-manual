# End-to-End Data Pipeline for Santa Lucía Lottery: Historical Data Mining, Web Scraping, ETL, and Dynamic Visualization

https://loteria.org.gt/site/award

### findings: 

1. By using the lottery id, I can iterate over the objects listed in the awards list.
by example here by using the id selector, is easy to look for the "Sortero Extraordinario N.390" because it has the `id=177`
Also in many cases is easy to guess what will be the next URL because all the "Sorteos Ordinarios" have a consecutive number like: `180`,`181`,`183`,`184`.
While the "Sorteos Extraordinarios" have these kind of numbers: `177`,`182`,`188`,`192`

So we will look for the new list awards by using the "id", 

2. 


Xpaths "Listado de premios" https://loteria.org.gt/site/award
<a href="/site/award-detail?id=177&amp;sorteo=390&amp;TipoSorteo=Extraordinario"></a>


working into the data base in AWS


Sorteos Extraordinarios have a max of 90,000 tickets sold for each lottery
Sorteos Ordinarios have a max of 80,000 tickets sold for each lottery



### At least in my investigation I saw that in 2025 Loteria Santa Lucia showed this message: 

¡Bienvenido!, de acuerdo a regulaciones de la Contraloría General de Cuentas y las regulaciones del Código Civil Decreto Ley Número 106, Artículo 2139, los sorteos se realizarán cuando se alcancen el 80% de la venta de los billetes emitidos.

Agradecemos la confianza en Lotería Santa Lucía.

Meaning: they are going to do the lottery only when they reach the 80% of the tickets sold. I did not see this in 2024