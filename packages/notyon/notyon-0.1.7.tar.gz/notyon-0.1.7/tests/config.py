# load dotenv file
from dotenv import load_dotenv
import notyon as Notion
import os
load_dotenv()

# Configuration
token = os.getenv("NOTION_ACCESS_TOKEN")
database_title = os.getenv("DATABASE_TITLE")
test_database_id = os.getenv('TEST_DATABASE_ID')
page_id = os.getenv('PAGE_ID')
client = Notion.client(token)