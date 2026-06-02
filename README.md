[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Server Tests](https://github.com/USEPA/haztrak/actions/workflows/test_server.yaml/badge.svg)](https://github.com/USEPA/haztrak/actions/workflows/test_server.yaml)
[![Client Tests](https://github.com/USEPA/haztrak/actions/workflows/test_client.yaml/badge.svg)](https://github.com/USEPA/haztrak/actions/workflows/test_client.yaml)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/USEPA/haztrak?label=latest%20release)](https://github.com/my-user/my-repo/releases/tag/v1.0.0)

[![Backend Framework](https://img.shields.io/badge/Django-RESTful_API-0C4B33?logo=django)](https://www.djangoproject.com/)
[![Frontend Framework](https://img.shields.io/badge/React-SPA-374151?logo=react)](https://reactjs.org/)
[![Database](https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql)](https://www.postgresql.org/)
[![Async Tasks](https://img.shields.io/badge/Celery-Async_Tasks-A9CC54?logo=celery)](https://www.postgresql.org/)

---

# Haztrak :recycle:

Haztrak is a web application for managing hazardous waste shipments with EPA's
[e-Manifest](https://github.com/USEPA/e-Manifest) / RCRAInfo systems — track waste
electronically from cradle-to-grave.

## Getting Started :rocket:

Run locally from the project root with:

```shell
npm install
npm start
```

Then open [http://localhost:3000](http://localhost:3000).

On first start the app migrates SQLite, seeds sample data when the database is empty, and
ensures local passwords for seed accounts:

| Username | Password |
|----------|----------|
| `testuser1` | `password1` |
| `admin` | `password1` |
| `orgadmin` | `password1` |

You can also register a new account from `/register`.

- See our [documentation](https://usepa.github.io/haztrak) for details
- [Contribution guidelines](https://github.com/USEPA/haztrak/blob/main/.github/CONTRIBUTING.md)
- [Issue tracker](https://github.com/USEPA/haztrak/issues)

### About e-Manifest

June 30, 2018. the U.S. Environmental Protection Agency (EPA) launched a national system for tracking hazardous waste shipments electronically,
this system, known as "[e-Manifest](https://www.epa.gov/e-manifest)," modernizes the nation’s paper-intensive process
for tracking hazardous waste from cradle to grave while saving valuable time, resources, and dollars for industry and
states.

e-Manifest, a modular component of [RCRAInfo](https://rcrainfo.epa.gov/), can be accessed by its users in two ways:

1. Through your favorite web browser at https://rcrainfo.epa.gov/
2. Via the RCRAInfo RESTful application programming interface (API)

Haztrak uses the API so handlers can work with electronic manifests without logging into RCRAInfo in a browser.
Enter RCRAInfo API credentials on the Profile page to enable live e-Manifest submit/sign/sync.

For more information on using the RCRAInfo and e-Manifest web services, please see the
[USEPA/e-Manifest](https://github.com/USEPA/e-manifest) repo or contact the
[e-Manifest Team](https://www.epa.gov/e-manifest/forms/contact-us-about-hazardous-waste-electronic-manifest-system).

## License

Haztrak is licensed under the [MIT open source](/LICENSE) license.

## Disclaimer

The United States Environmental Protection Agency (EPA) GitHub project code
is provided on an "as is" basis and the user assumes responsibility for its
use. EPA has relinquished control of the information and no longer has
responsibility to protect the integrity, confidentiality, or availability
of the information. Any reference to specific commercial products,
processes, or services by service mark, trademark, manufacturer, or
otherwise, does not constitute or imply their endorsement, recommendation
or favoring by EPA. The EPA seal and logo shall not be used in any manner
to imply endorsement of any commercial product or activity by EPA or
the United States Government.
