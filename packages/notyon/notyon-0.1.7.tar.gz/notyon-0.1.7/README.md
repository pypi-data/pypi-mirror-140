# Notyon
## Notion SDK for Python

![Notyon Logo](images/logo-notyon.png)

Notyon is an open source Python package that implements the [Notion API](https://developers.notion.com/reference/intro) in Python.

## Installation
Run the following command to install:
`pip install notyon`

## How to get your Notion auth token
Follow this tutorial: [Get your Notion auth token](docs/get_notion_token.md)

## Basic Example
```python
import notyon as Notion # Import Notyon

# Create an notion client instance
client = Notion.client("auth_token")

# Find a Database
# If found: Returns a Database instance
# If not found: Returns None
found_database = Notion.Database.find(client, "Database name")

# Get database info
db_title = found_database.title
db_id = found_database.id

# Retrieve database content
content = found_database.retrieve()

## Create a database
# If created: Returns a Database instance
# If didn't create: Returns None

# First, get the page_id (parent)[
page_id = "page-id-example"

# Second, create the model
model = Notion.Model("Database title")
model.add([
    #{"field name": "field type"}
    {"name": "text"},
    {"description": "rich_text"}
])

created_database = Notion.Database.create(client, page_id, model)
```

## Roadmap 🗺️
- 🗃️ Database 1 (v0.1)
    - [x] Retrieve
    - [x] Create

- 🗃️ Database 2 (v0.2)
    - [ ] Update
    - [ ] Query

- 📄 Pages 1 (v0.3)
    - [ ] Retrieve
    - [ ] Create
    - [ ] Delete

- 📄 Pages 2 (v0.4)
    - [ ] Update
    - [ ] Query

- 🔳 Blocks 1 (v0.5)
    - [ ] Retrieve
    - [ ] Create

- 🔳 Blocks 2 (v0.6)
    - [ ] Update
    - [ ] Query

- 👤 Users (v0.7)
    - [ ] Retrieve an user
    - [ ] List

- 🔍️ Search (v0.8)
    - [ ] Query pages

- 🖇️ [Retrieve a page property item](https://developers.notion.com/reference/retrieve-a-page-property) (0.9)
- 🔑 [Retrieve your token's bot user](https://developers.notion.com/reference/get-self) (1.0)
