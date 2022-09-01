# Local Development Environment

## Starting local development environment

1. From the root of this repo navigate to the liferay folder:

    `cd liferay`

2. Start docker-compose there:

    `docker-compose up`

3. On the first run it will then download the docker images, set up mysql and then start Liferay. During the Liferay start it will fill the database with the initial data.

## Remove volumes

If you want to start liferay / db from scratch you can remove the volumes and then start again:

`docker-compose down -v`

## Importer config

1. Copy the `config.json` in the root of the repo to `config.local.json`. This file will store the authentication information for the importer and should _NOT_ be checked in. For other environments you can create alternate config files like `config.lxc.json`. These can be used by passing in the `--config` option to any of the python scripts (e.g. `python3 import_learn.py --config ./config.lxc.json`)

## Initial Liferay setup

### OAuth Setup

1. Visit http://localhost:8080 and log in as `test@liferay.com` with password `test`
2. Change the password to something you can remember
3. Accept Terms of Use
4. Go to Control Panel -> OAuth 2 Administration
5. Create a new OAuth 2 Application with the name "Learn Import"
6. Change client profile to "Headless Server" and Save
7. After saving, edit the OAuth 2 Application you just created. Navigate to the "Scopes" tab and click the following and then Save

-   `LIFERAY.HEADLESS.DELIVERY` - click all the three options
    -   `Liferay.Headless.Delivery.everything`
    -   `Liferay.Headless.Delivery.everything.read`
    -   `Liferay.Headless.Delivery.everything.write`
-   `PORTAL SERVICES`
    -   `liferay-json-web-services.everything.write`
    -   `liferay-json-web-services.everything`
-   `LIFERAY.DATA.ENGINE.REST` - click all three options

8. Open up the OAuth 2 Application again and copy the values for `Client ID` and `Client Secret`. Add these values to `config.local.json`

### Structure and file entry type setup

1. To find the group Id of your Liferay instance navigate to `Configuration` -> `Site Settings` in the side nav and note the URL which will contain the group ID. Store this value in `config.local.json` (`SITE_ID`)

2. Run the python script `site_setup.py` to create the learn article structure and the file entry type.

    `python3 site_setup.py`

### Building sphinx site

1. Clone this branch https://github.com/allen-ziegenfus/liferay-learn/tree/sphinx-json-builder

2. Navigate to the site directory

    `cd site`

3. Invoke the sphinx build with the dxpimportjson option

    `./build_site.sh dxpimportjson`

4. If everything succeeds there should be files created under `site/build/output`. Configure the full path to this directory in your `config.local.json` (`SPHINX_OUTPUT_DIRECTORY`)

### Running the import script

1. Prepare the python environment

    `pipenv shell`

2. Review your configuration file (i.e. `config.local.json`). To just import a few articles / documents you can set the following. Otherwise it will import the whole site which may take a long time (45 minutes on LXC)

    "DOCUMENT_IMPORT_LIMIT": 5,
    "ARTICLE_IMPORT_LIMIT": 5,

3. Run the import script

    `python3 import_learn.py`

# Python Development

## Install new packages

`pipenv install requests`

## Formatting

The python code is formatted using black
