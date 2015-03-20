Copyright 2014 NPR.  All rights reserved.  No part of these materials may be reproduced, modified, stored in a retrieval system, or retransmitted, in any form or by any means, electronic, mechanical or otherwise, without prior written permission from NPR.

(Want to use this code? Send an email to nprapps@npr.org!)


carebot
========================

* [What is this?](#what-is-this)
* [Assumptions](#assumptions)
* [Bootstrap the project](#bootstrap-the-project)
* [Hide project secrets](#hide-project-secrets)
* [Run the project](#run-the-project)
* [Deploy to EC2](#deploy-to-ec2)
* [Run a remote fab command](#run-a-remote-fab-command)

What is this?
-------------

Carebot cares about us so much it automatically reports out, summarizes and sends us our analytics.

For documentation of the metrics and queries used see the [reports](https://github.com/nprapps/reports#google-metrics-we-care-about) repo.

Assumptions
-----------

The following things are assumed to be true in this documentation.

* You are running OSX.
* You are using Python 2.7. (Probably the version that came OSX.)
* You have [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) installed and working.
* You have NPR's AWS credentials stored as environment variables locally.

For more details on the technology stack used with the app-template, see our [development environment blog post](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html).

Bootstrap the project
---------------------

```
cd carebot
mkvirtualenv carebot
pip install -r requirements.txt
fab data.local_reset_db data.bootstrap_db
python manage.py collectstatic
```

**Problems installing requirements?** You may need to run the pip command as ``ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install -r requirements.txt`` to work around an issue with OSX.

Hide project secrets
--------------------

Project secrets should **never** be stored in ``app_config.py`` or anywhere else in the repository. They will be leaked to the client if you do. Instead, always store passwords, keys, etc. in environment variables and document that they are needed here in the README.

Run the project
---------------

```
workon $PROJECT_SLUG
fab public_app
```

Visit [localhost:8000](http://localhost:8000) in your browser.

Deploy to EC2
-------------

One time setup:

```
fab staging master servers.setup
fab staging master data.server_reset_db
fab staging master servers.fabcast:data.bootstrap_db
```

Routine deployment:

```
fab staging master deploy
```

Run a  remote fab command
-------------------------

Sometimes it makes sense to run a fabric command on the server, for instance, when you need to render using a production database. You can do this with the `fabcast` fabric command. For example:

```
fab staging master servers.fabcast:cron_jobs.run_reports
```

If any of the commands you run themselves require executing on the server, the server will SSH into itself to run them.
