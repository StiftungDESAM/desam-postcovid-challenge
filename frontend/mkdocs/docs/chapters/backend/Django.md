## Django

The entire backend is written using the Python web framework Django. The two core components of the graph database and the API are described in separate sections. The purpose of this chapter is to gather some Django-specific information that might be relevant to developers.

### Admin panel

The Django admin panel can be found at the sub-URL `/admin`. An admin account is required to access it. For testing it's recommended to user the mock_users command to create test users and then log in using the credentials `super_admin@example.com` with the password `x`.

Django models must explicitly be registered in the `admin.py` of the corresponding app to appear there.


### Custom management commands
Django management commands can modify the data in the backend while it's running. They're also commonly used for initialization by calling them from the entrypoint script. As a developer, you can run management commands in your running Docker container with the following shell command:
`docker exec -it postcovid_backend python manage.py <custom command and its parameters>`

#### mock_users
This command creates a mock user for each role that exists in the backend for testing purposes. This command is only enabled when the server runs in DEBUG mode. The usernames of all created users are `<role>@example.com` and the password is `x`.
It's recommended to add the `--verified` flag to the command which automatically grants the mock users their permissions, otherwise this must be done manually.
The account `super_admin@example.com` is created as a superuser and the account `admin@example.com` as a staff member but not a superuser.

#### load_constants
Constants like the list of available permissions and user roles must be initialized in the database at some point.  To avoid unnecessary database migrations, this command automatically checks if all defined constants are in the database and creates them otherwise.

*This command is called automatically during server startup.*

#### migrate_graph_database
The graph database is managed by the package "neomodel". At server startup, neomodel must apply all database indices and constraints to the graph database.
As the labels for the knowledge graph are generated dynamically from the ontology graph, this custom command is required to include them in this initialization.

*This command is called automatically during server startup.*
