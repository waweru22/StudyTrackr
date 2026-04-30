# Dev Scripts

These are manual verification and testing scripts used during development.

DO NOT run these against a live or demo database — many of them call
service functions directly (end_session, generate_schedule, etc.) which
will create real database records including notifications, XP awards,
and streak changes.

These scripts are quarantined here and are not part of the application.
After the demo they should be reviewed and either converted to proper
pytest unit tests or deleted.
