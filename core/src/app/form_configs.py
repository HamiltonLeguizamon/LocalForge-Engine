"""
Form configurations and schemas for projects.
"""

def get_flask_cookiecutter_config(template_url=None):
    """Returns the field configuration for Flask cookiecutter."""
    return [
        {
            "name": "full_name",
            "label": "Full name",
            "type": "text",
            "default": "Developer",
            "placeholder": "Your full name",
            "required": False
        },
        {
            "name": "email",
            "label": "Email",
            "type": "email",
            "default": "dev@example.com",
            "placeholder": "you@email.com",
            "required": False
        },
        {
            "name": "github_username",
            "label": "GitHub username",
            "type": "text",
            "default": "developer",
            "placeholder": "github_username",
            "required": False
        },
        {
            "name": "project_name",
            "label": "Project name",
            "type": "text",
            "default": "",
            "placeholder": "My Flask Project",
            "required": True
        },
        {
            "name": "app_name",
            "label": "Technical name",
            "type": "text",
            "default": "",
            "placeholder": "my_flask_project",
            "required": True
        },
        {
            "name": "project_short_description",
            "label": "Description",
            "type": "textarea",
            "default": "",
            "placeholder": "An amazing Flask application",
            "required": False
        },
        {
            "name": "use_pipenv",
            "label": "Use Pipenv",
            "type": "select",
            "default": "n",
            "options": [
                {"value": "y", "label": "Yes"},
                {"value": "n", "label": "No"}
            ],
            "required": False
        },
        {
            "name": "python_version",
            "label": "Python version",
            "type": "select",
            "default": "3.11",
            "options": [
                {"value": "3.9", "label": "Python 3.9"},
                {"value": "3.10", "label": "Python 3.10"},
                {"value": "3.11", "label": "Python 3.11"},
                {"value": "3.12", "label": "Python 3.12"},
                {"value": "custom", "label": "Custom"}
            ],
            "required": False
        },
        {
            "name": "python_version_custom",
            "label": "Custom Python version",
            "type": "text",
            "default": "",
            "placeholder": "3.13, 3.8, etc.",
            "required": False,
            "depends_on": "python_version",
            "depends_value": "custom"
        },
        {
            "name": "node_version",
            "label": "Node.js version",
            "type": "select",
            "default": "18",
            "options": [
                {"value": "16", "label": "Node.js 16"},
                {"value": "18", "label": "Node.js 18"},
                {"value": "20", "label": "Node.js 20"},
                {"value": "custom", "label": "Custom"}
            ],
            "required": False
        },
        {
            "name": "node_version_custom",
            "label": "Custom Node.js version",
            "type": "text",
            "default": "",
            "placeholder": "14, 21, latest, etc.",
            "required": False,
            "depends_on": "node_version",
            "depends_value": "custom"
        },
        {
            "name": "use_heroku",
            "label": "Configure Heroku",
            "type": "select",
            "default": "n",
            "options": [
                {"value": "y", "label": "Yes"},
                {"value": "n", "label": "No"}
            ],
            "required": False
        }
    ]

def get_django_cookiecutter_config(template_url=None):
    """Returns the field configuration for cookiecutter Django."""
    return [
        {
            "name": "project_name",
            "label": "Project name",
            "type": "text",
            "default": "",
            "placeholder": "My Django Project",
            "required": True
        },
        {
            "name": "project_slug",
            "label": "Technical name (slug)",
            "type": "text",
            "default": "",
            "placeholder": "my_django_project",
            "required": True
        },
        {
            "name": "description",
            "label": "Project description",
            "type": "textarea",
            "default": "",
            "placeholder": "An amazing web application with Django",
            "required": False
        },
        {
            "name": "author_name",
            "label": "Author name",
            "type": "text",
            "default": "Developer",
            "placeholder": "Your full name",
            "required": False
        },
        {
            "name": "email",
            "label": "Email",
            "type": "email",
            "default": "dev@example.com",
            "placeholder": "you@email.com",
            "required": False
        },
        {
            "name": "domain_name",
            "label": "Domain name",
            "type": "text",
            "default": "example.com",
            "placeholder": "mydomain.com",
            "required": False
        },
        {
            "name": "version",
            "label": "Initial version",
            "type": "text",
            "default": "0.1.0",
            "placeholder": "0.1.0",
            "required": False
        },
        {
            "name": "open_source_license",
            "label": "Open source license",
            "type": "select",
            "default": "1",
            "options": [
                {"value": "1", "label": "MIT"},
                {"value": "2", "label": "BSD"},
                {"value": "3", "label": "GPLv3"},
                {"value": "4", "label": "Apache Software License 2.0"},
                {"value": "5", "label": "Not open source"}
            ],
            "required": False
        },
        {
            "name": "username_type",
            "label": "Username type",
            "type": "select",
            "default": "1",
            "options": [
                {"value": "1", "label": "username"},
                {"value": "2", "label": "email"}
            ],
            "required": False
        },
        {
            "name": "timezone",
            "label": "Timezone",
            "type": "select",
            "default": "UTC",
            "options": [
                {"value": "UTC", "label": "UTC"},
                {"value": "America/New_York", "label": "America/New_York"},
                {"value": "America/Chicago", "label": "America/Chicago"},
                {"value": "America/Denver", "label": "America/Denver"},
                {"value": "America/Los_Angeles", "label": "America/Los_Angeles"},
                {"value": "Europe/Madrid", "label": "Europe/Madrid"},
                {"value": "Europe/London", "label": "Europe/London"},
                {"value": "Asia/Tokyo", "label": "Asia/Tokyo"}
            ],
            "required": False
        },
        {
            "name": "windows",
            "label": "Windows support",
            "type": "select",
            "default": "n",
            "options": [
                {"value": "y", "label": "Yes"},
                {"value": "n", "label": "No"}
            ],
            "required": False
        },
        {
            "name": "editor",
            "label": "Preferred editor",
            "type": "select",
            "default": "3",
            "options": [
                {"value": "1", "label": "None"},
                {"value": "2", "label": "PyCharm"},
                {"value": "3", "label": "VS Code"}
            ],
            "required": False
        },
        {
            "name": "use_docker",
            "label": "Use Docker",
            "type": "select",
            "default": "y",
            "options": [
                {"value": "y", "label": "Yes (Recommended)"},
                {"value": "n", "label": "No"}
            ],
            "required": False
        },
        {
            "name": "postgresql_version",
            "label": "PostgreSQL version",
            "type": "select",
            "default": "2",
            "options": [
                {"value": "1", "label": "15"},
                {"value": "2", "label": "16"},
                {"value": "3", "label": "17"}
            ],
            "required": False
        },
        {
            "name": "cloud_provider",
            "label": "Cloud provider",
            "type": "select",
            "default": "4",
            "options": [
                {"value": "1", "label": "AWS"},
                {"value": "2", "label": "GCP"},
                {"value": "3", "label": "Azure"},
                {"value": "4", "label": "None"}
            ],
            "required": False
        },
        {
            "name": "mail_service",
            "label": "Email service",
            "type": "select",
            "default": "9",
            "options": [
                {"value": "1", "label": "Mailgun"},
                {"value": "2", "label": "Amazon SES"},
                {"value": "3", "label": "Mailjet"},
                {"value": "4", "label": "Mandrill"},
                {"value": "5", "label": "Postmark"},
                {"value": "6", "label": "Sendgrid"},
                {"value": "7", "label": "SendinBlue"},
                {"value": "8", "label": "SparkPost"},
                {"value": "9", "label": "Other SMTP"}
            ],
            "required": False
        },
        {
            "name": "use_async",
            "label": "Use async support",
            "type": "select",
            "default": "n",
            "options": [
                {"value": "y", "label": "Yes"},
                {"value": "n", "label": "No"}
            ],
            "required": False
        },
        {
            "name": "use_drf",
            "label": "Use Django REST Framework",
            "type": "select",
            "default": "n",
            "options": [
                {"value": "y", "label": "Yes"},
                {"value": "n", "label": "No"}
            ],
            "required": False
        },
        {
            "name": "frontend_pipeline",
            "label": "Frontend pipeline",
            "type": "select",
            "default": "1",
            "options": [
                {"value": "1", "label": "None"},
                {"value": "2", "label": "Django Compressor"},
                {"value": "3", "label": "Gulp"},
                {"value": "4", "label": "Webpack"}
            ],
            "required": False
        },
        {
            "name": "use_celery",
            "label": "Use Celery",
            "type": "select",
            "default": "n",
            "options": [
                {"value": "y", "label": "Yes"},
                {"value": "n", "label": "No"}
            ],
            "required": False
        },
        {
            "name": "use_mailpit",
            "label": "Use Mailpit for development",
            "type": "select",
            "default": "n",
            "options": [
                {"value": "y", "label": "Yes"},
                {"value": "n", "label": "No"}
            ],
            "required": False
        },
        {
            "name": "use_sentry",
            "label": "Use Sentry for monitoring",
            "type": "select",
            "default": "n",
            "options": [
                {"value": "y", "label": "Yes"},
                {"value": "n", "label": "No"}
            ],
            "required": False
        },
        {
            "name": "use_whitenoise",
            "label": "Use WhiteNoise for static files",
            "type": "select",
            "default": "y",
            "options": [
                {"value": "y", "label": "Yes (Recommended)"},
                {"value": "n", "label": "No"}
            ],
            "required": False
        },
        {
            "name": "use_heroku",
            "label": "Configure for Heroku",
            "type": "select",
            "default": "n",
            "options": [
                {"value": "y", "label": "Yes"},
                {"value": "n", "label": "No"}
            ],
            "required": False
        },
        {
            "name": "ci_tool",
            "label": "CI/CD tool",
            "type": "select",
            "default": "1",
            "options": [
                {"value": "1", "label": "None"},
                {"value": "2", "label": "Travis"},
                {"value": "3", "label": "Drone"},
                {"value": "4", "label": "GitHub"},
                {"value": "5", "label": "GitLab"}
            ],
            "required": False
        },
        {
            "name": "keep_local_envs_in_vcs",
            "label": "Keep local .env files in version control",
            "type": "select",
            "default": "y",
            "options": [
                {"value": "y", "label": "Yes"},
                {"value": "n", "label": "No"}
            ],
            "required": False
        },
        {
            "name": "debug",
            "label": "Enable debug mode",
            "type": "select",
            "default": "n",
            "options": [
                {"value": "y", "label": "Yes"},
                {"value": "n", "label": "No"}
            ],
            "required": False
        }
    ]
