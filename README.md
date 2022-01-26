# Greynoise-Discord-Alerts

[![alert_scheduler](https://github.com/ThreatDudes/Greynoise-Discord-Alerts/actions/workflows/alert_scheduler.yml/badge.svg?event=schedule)](https://github.com/ThreatDudes/Greynoise-Discord-Alerts/actions/workflows/alert_scheduler.yml)

Sends Greynoise query results to a Discord channel on a scheduled basis.

## Adding Greynoise Key and Discord Webhook URL to repo environment variables
You are going to need the following items:
- `GREYNOISE_API_KEY`: an API key from your [GreyNoise](https://www.greynoise.io/viz/) account.
- `DISCORD_WEBHOOK_URL`: a Discord Webhook endpoint that is specific to the Discord server and channel.

GreyNoise API keys are available at Community and Enterprise levels. [Go to your account details to get your key.](https://www.greynoise.io/viz/account/)

[Read here on how to generate a Discord webhook url.](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

Once you have forked this project to your own repository, you can start setting the environment variables and the GitHub Actions. You must then save both the GreyNoise API key and Discord URL to your new porject repository as **Repository Secrets for GitHub Actions**. Read here for the instructions on adding them to your repository: [Creating encrypted secrets for GitHub Actions](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository).

## Adding new queries
To add a new query, simply past a [`GNQL` query](https://github.com/GreyNoise-Intelligence/GNQL) into a file with a useful name, e.g. `maliciousNonBot.gnql` or `firstSeen_1d.gnql`.

## Scheduling new reports
You must use the syntax of GitHub actions to schedule new alerts.

1. Go to `.github/workflows/alert_scheduler.yml` in the GitHub hidden directory.
2. Paste a new step to run with a proper `if` condition and correct `gnql` file to point to.
3. commit changes and push to the directory.

New automated jobs have a syntax like this:
```
- name: NewQueryName
if: github.event.schedule = '0 14 * * *'
env:
    GREYNOISE_API_KEY: ${{ secrets.GREYNOISE_API_KEY }}
    DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
run: python3 run-greynoise-query.py gnql/NewQueryName.gnql
```
The `if` statement refers to which of the above cron schedules in the `on` section to watch for. If there isn't a schedule timing you like, just append a new one and match it to the `if` statement.

## References
- [GitHub Actions - `Schedule` Event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)
- [GreyNoise Query Language](https://github.com/GreyNoise-Intelligence/GNQL)