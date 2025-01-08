# End-to-End Data Pipeline for Santa Lucía Lottery: Historical Data Mining, Web Scraping, ETL, and Dynamic Visualization

## **Description:** 

In this project I tried to answer and discover insights about **"Loteria Santa Lucia de Guatemala"** which is the biggest lottery in my country (Guatemala). Also to create a historical dataset for their winnig number, due to the fact that there is no way to retrieve the old data from the past draws.

## **Table of contents**

Pending...

## **Why of this project?**

Lotería Santa Lucía is the largest and oldest lottery in Guatemala, founded in 1956. Unfortunately, there is no way to retrieve historical data other than through old physical newspapers, some Facebook videos (available only since 2018), or by purchasing old newspapers (PDFs) from the "National Newspaper Archive of Guatemala," which is very expensive (I tried it...).

Once a draw expires, the data is permanently erased. There is no way to perform any kind of audit on "Lotería Santa Lucía." Surprisingly, no thesis projects or university studies from Math or Statistics students have been conducted on this topic. Additionally, there is no dataset available on platforms like Kaggle.

Due to all these factors, I found a valuable way to provide data that no one else has, which could be interesting for those interested in statistics and Machine Learning.


## **Automated ETL Process for Loteria Santa Lucia Data**

### Introduction

This project focuses on automating the ETL (Extract, Transform, Load) process for Santa Lucia Lottery data. The main goal is to efficiently collect, clean, and store data to enable analysis and visualization, highlighting insights such as winning patterns, frequently rewarded locations, and more.

### ETL Architecture

The ETL process consists of three primary stages:

1. **Extraction:** Retrieving raw lottery data from the web.

2. **Transformation:** Cleaning, structuring, and enriching the data.

3. **Load:** Storing the processed data into a database and locally for further use.

Below is a high-level overview of the workflow:

> [Extract raw data from the web] --> [Transform into structured datasets] --> [Load into AWS RDS]


### Extract Phase 

**Overview**

* **Tool Used:** Selenium with Python.
* **Purpose:** Scrape lottery data from the Santa Lucia lottery website.
* **Process:**

    * Open the lottery awards website.
    * Navigate to the desired draw information using a lottery ID.
    * Extract header and body data (prizes, winning numbers).
    * Save the extracted content to a .txt file for processing.
    

















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