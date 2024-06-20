---
---

# Food warnings <Badge type="warning" text="in development" />

> A sensor to read out the current food warnings in the region.

## Official german warning site

Currently there is a website that shows the warnings. [https://www.lebensmittelwarnung.de](https://www.lebensmittelwarnung.de/)

### Filtering data

The website adds the filter to the URI. So with detailled link we can only read out the warnings that we want
Example for Baden-Württemberg:

```http
https://www.lebensmittelwarnung.de/SiteGlobals/Forms/Suche/Expertensuche/Expertensuche_Formular.html?cl2Taxonomies_Bundeslaender=%22%2Fc%2Fbundeslaender%2Fbaden-wuerttemberg%22&cl2Taxonomies_Grund=%22%2Fc%2Fgrund%2Fallergene%22+%22%2Fc%2Fgrund%2Ffremdkoerper%22+%22%2Fc%2Fgrund%2Fgesundheitsschaedlichesubstanz%22+%22%2Fc%2Fgrund%2Firrefuehrungundtaeuschung%22+%22%2Fc%2Fgrund%2Fkrankheitserreger%22+%22%2Fc%2Fgrund%2Frueckstaendeundkontaminaten%22+%22%2Fc%2Fgrund%2Fsonstigegruende%22&dateOfIssueQuery=lastSevenDays
```

In Detail we have following Filters.

::: code-group

```text [Reason filter]
cl2Taxonomies_Grund="%2Fc%2Fgrund%2Fallergene"+"%2Fc%2Fgrund%2Ffremdkoerper"+"%2Fc%2Fgrund%2Fgesundheitsschaedlichesubstanz"+"%2Fc%2Fgrund%2Firrefuehrungundtaeuschung"+"%2Fc%2Fgrund%2Fkrankheitserreger"+"%2Fc%2Fgrund%2Frueckstaendeundkontaminaten"+"%2Fc%2Fgrund%2Fsonstigegruende"
```

```text [Region filter]
cl2Taxonomies_Bundeslaender="%2Fc%2Fbundeslaender%2Fbaden-wuerttemberg"
```

```text [Date Filter]
dateOfIssueQuery=lastSevenDays
```

:::

## How to integrate in home assistant?

### Ideas

#### How to get the data

- using the multiscraping integration
- finding a api and using the rest integration

#### Features

- showing the alerts in the UI
- notification when new alert is published?
