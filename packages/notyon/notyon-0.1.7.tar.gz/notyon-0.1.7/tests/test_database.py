import notyon as Notion
import config

def test_database_retrieve():
    """
    Tests database_retrieve() function
    Tests if it doesn't return an error
    Tests if it does return an error
    """
    database_id = config.test_database_id

    database = Notion.Database.find(config.client, config.database_title);
    content = database.retrieve();

    assert content != None

def test_search():
    """
    Test if the search database by title is performing correctly
    """

    response = Notion.Database.find(config.client, config.database_title)
    nonexistent_title = Notion.Database.find(config.client, "This title does not exist")

    assert response.title != None
    assert nonexistent_title == None

def test_create():
    """
        Test Database creation
    """

    model = Notion.Model("To do list")

    model.add([
        {"task": "title"},
        {"description": "rich_text"}
    ]);

    response = Notion.Database.create(config.client, config.page_id, model);

    assert response != None;