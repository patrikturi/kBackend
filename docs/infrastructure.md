# Infrastructure
| What | Where | Project Name or Folder | Account | Subscription | Comments |
|---|---|---|---|---|---|
| Source code | GitHub | https://github.com/patrikturi/kBackend | patrik.turi.0xff@gmail.com | - | Can invite other users or fork the repo |
| Domain name | Hostinger | hostinger.com -> ksoccersl.com | patrik.turi.0xff@gmail.com | -2021-09 | Can transfer domain to other account if needed |
| SSL Certificate | Hostinger | https://backend.ksoccersl.com | patrik.turi.0xff@gmail.com | -2021-09 | Don't need a certificate for the primary domain because Firebase provides it out of the box. Check next year if we could use a "Let's encrypt" free certificate instead or it is worth renewing this. |
| Cloud Provider | AWS | ksoccer-dev@outlook.com | Free tier until 2021-09 | Can create/invite admin or limited IAM accounts |
| Server | AWS EC2 |  |  |  |
| Secrets | AWS S3 | kbackend-secrets |  |  |
| Sentry | sentry.io | kSoccer | ksoccer-dev@outlook.com |  |
TODO: logs, backup, database

# Server
* gunicorn <-> django
* Currently does not use Nginx because:
  * One less component to configure and break
  * Static assets are served by CDN (except the Admin but that has very few users)
  * Can add Nginx to the host later if needed (eg. show an "Under maintenance" page)
