[![Hexlet Ltd. logo](https://tt-data.tutortop.ru/schools/nbEwzprIgDPTDIwpsNTHcA8I20i3le6pDVFxmyuU.png)](https://ru.hexlet.io/pages/about?utm_source=github&utm_medium=link&utm_campaign=python-package)

# The Page Analyzer package

[![Actions Status](https://github.com/Dmitriy-Parfimovich/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/Dmitriy-Parfimovich/python-project-83/actions)
[![Workflow status](https://github.com/Dmitriy-Parfimovich/python-project-83/actions/workflows/page_analyzer-check.yml/badge.svg)](https://github.com/Dmitriy-Parfimovich/python-project-83/actions)

<h1 align="center">The Page Analyzer package</h1>

This is a hexlet courses educational project.
The Page Analyzer is a website that analyzes the specified pages for SEO suitability.
In case the site is available, we get its: 
- response code
- "<h1>" tag;
- "<title>" tag;
- "<meta name="description" content="...">" tag.
The project is based on Flask-framework: HTTP-requests and routing. The results of the checks are recorded in the database.

You can see the project [here](https://python-project-83-production-6014.up.railway.app) 

## Instalation

```sh
git clone <package>
pip install poetry
make install
```

## Requirements

- Python 3.8
- Poetry 1.1.13
- Flask 2.3.2
- PostgreSQL 12.14