import os
import sys

from notion_client import Client  # ,AsyncClient


try:
    notion_client_object = Client(auth=os.environ["NOTION_TOKEN"])
except Exception:
    print("Notion Integration Token is not found")
    print(
        """
        Welcome to notion2md!

        To get started, you need to save your Notion Integration Token.
        Find your token at

            https://www.notion.so/my-integrations

        Then run shell command:

            $export NOTION_TOKEN="<Your Token>"

        If you want to save this environment variable after reboot,
        put upper command in your shell resource(ex: .bashrc or .zshrc)
    """
    )
    sys.exit(1)
# notion_async_client = AsyncClient(auth=os.environ["NOTION_TOKEN"])


def get_children(parent_id):
    return notion_client_object.blocks.children.list(parent_id)["results"]
