# Salon kaukolämpö Home Assistantissa

[English](README.md) | [Suomi](README.fi.md) | [Svenska](README.sv.md)

![Project logo](custom_components/salon_district_heating/brand/icon.png)

Epävirallinen MIT-lisensoitu integraatio Salon Kaukolämmön LämpöVahti-rajapintaan. Tarkoitus ei ole korvata Lämpövahtia, vaan tuoda kaukolämpödata Home Assistantiin rakennuksen energiatehokkuuden analysointia varten.

**Tila:** 0.1.0-alpha.4, kokeellinen. Testattu erillisessä Home Assistant -ympäristössä. Tuotantoasennuksen ja energianäkymän testaus on kesken. Projekti on energiayhtiöstä riippumaton.

## API-avain

1. Kirjaudu [Lämpövahtiin](https://lampovahti.salonkaukolampo.fi/login).
2. Avaa Tilini → API-avaimet.
3. Valitse Luo uusi avain. Säilytä avain salassa. Jos käyttöoikeus puuttuu, ota yhteyttä energiayhtiöön.

## Asennus testaajille

Alustava yhteensopivuustavoite on Home Assistant 2026.11.0. Varmuuskopioi asetukset. Kopioi repositorion `custom_components/salon_district_heating`-hakemisto Home Assistantin asetushakemiston `custom_components`-hakemistoon. Käynnistä Home Assistant uudelleen. Valitse Asetukset → Laitteet ja palvelut → Lisää integraatio → Salon Kaukolämpö. Syötä API-avain ja valitse käyttöpaikka. YAML-asetuksia ei tarvita.

Yhteisöjakelun metatiedot on valmisteltu, mutta jakelukäyttöliittymän kautta tapahtuvaa asennusta ja katalogiin hyväksyntää ei ole vielä vahvistettu.

## Sensorit ja rajoitukset

Kumulatiivinen energia (kWh), tuntienergia (kWh), tunnin keskiteho (kW), meno- ja paluulämpötila (°C), lämpötilaero (K), virtaus (m³/h), mittausaika, lukeman tila, kulutusmittauksen aika ja datan laatu.

Havaittu energiaresoluutio on 1 kWh. Tunnin keskiteho ei ole hetkellinen teho. Viivästynyt tai ristiriitainen kulutus voi säilyttää viimeisen vahvistetun arvon enintään kaksi tuntia sen mittausajasta. Tarkista datan laatu ja kulutuksen mittausaika. Ei interpolointia. Älä käytä ainoana tietolähteenä reaaliaikaisessa lämmityksen ohjauksessa tai turvatoiminnoissa.

Tiedonkeruu alkaa asennuksesta. Ei historiatietojen tuontia, erillistä tietokantaa tai tariffilaskentaa. Home Assistant hallitsee historiansa ja tilastonsa. Energianäkymän yhteensopivuus on testattavana.

## Dokumentaatio

[Virallinen API](https://api-lampovahti.salonkaukolampo.fi/external/api/docs/) · [API-tiedot](docs/API_DATA.md) · [Arkkitehtuuri](docs/ARCHITECTURE.md) · [Mittausrajoitukset](docs/CONSUMPTION_INTEGRITY.md) · [Jakelu](docs/DISTRIBUTION.md)

Älä julkaise API-avaimia, osoitteita, mittarin sarjanumeroita tai tunnistettavia lokeja. Ilmoita ongelmista anonymisoituina GitHubissa. [MIT-lisenssi](LICENSE).
