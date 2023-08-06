# NOTIONPY
NOTIONPY uses notion api to add data to dataset



## Quickstart
Note:
Need the latest version of NOTIONPY requires Python 3.5 or greater.
- Get your token from [notion my-integrations](https://www.notion.so/my-integrations)
- Create the dataset in notion, and share the current dataset with my-integration 
<img src="https://github.com/wuchangsheng951/NOTIONPY/blob/main/share_example_invite.png" width="440">

- copy the dataset id from URL

```
URL = https://www.notion.so/username/31e877cc74d541f7bb2f06e4708e242c?v=39844aa472bc40989d97f85ec46ef1bd
datasetID = 31e877cc74d541f7bb2f06e4708e242c
```

## Usage

```
from NotionPy import NOTIONPY

# Get database ID from page URL
no = NOTIONPY(token,databaseId)

# update notion dataset column
no.update_column(['iou','data])

# update the value
no.add_col_value({'iou':'33',"Name":'hul2u','data':'233s2'})

```
