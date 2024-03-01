# AzureDevOpsConnector
A Python connector to return Work Item information across all projects within your Azure DevOps tenancy.

It makes use of the Azure DevOps Python library to retrieve a list of **bug** work items for all projects within your targeted tenancy. You can change this using the WIQL query to return other types of work item. You can also remove that filter entirely, but there is a 20k limit on returning work items. Additionally, you can only retrieve work item info for items in batches of up to 200 (I have handled this by batching them into groups of 200 before retrieving the information for each batch.)

You will need:
1. A Personal Access Token - you can get this from your Azure DevOps tenant if you look in your settings. The account you get the token from will require access to read the work items.
2. Organisation URL - you will need to specify your Azure DevOps organisation URL.

When retrieving the list of Work Item IDs from the workitems table, it uses a WIQL query (proprietary version of SQL). You can change this query to return different sets of items. In this case, I'm returning all work items where workitemtype = Bug and I'm doing this for every project within my tenancy: 

WIQL query: wiqlQuery = Wiql(query=f"SELECT * FROM workitems WHERE [System.TeamProject] = '{project.name}' AND [System.WorkItemType] = 'Bug'")

You could change the above to return a specified project only: 
YOUR_PROJECT = 'project name'
SELECT * FROM workitems WHERE [System.TeamProject] = 'YOUR_PROJECT' AND [System.WorkItemType] = 'Bug'

Or, to only return user stories:
SELECT * FROM workitems WHERE [System.TeamProject] = '{project.name}' AND [System.WorkItemType] = 'User Story'

It uses Pandas to load the data into a Dataframe and then transform it by removing unneeded columns (you can change the list to fit your needs) and then renames the columns to make them more presentable for visualisation.

**Power BI implementation**
You can use this to pull data into Power BI.

1. Go to data sources
2. Select Python script as source
3. Ensure you have a local Python environment installed and have the dependencies installed from the requirements.txt file
4. Set your script as the following:
   location = r'FILELOCATION' (replace FILELOCATION with where you have saved the Python file)

   exec(open(location).read())
5. Load in the data. Because it has been pre-transformed, it should be pretty much readily organised for you to start visualising. Would recommend either creating measures in Pandas first or using DAX if you prefer that.
