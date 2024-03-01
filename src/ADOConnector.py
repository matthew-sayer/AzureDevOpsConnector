from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking.models import Wiql
import pandas as pd

patToken = '<token>' #Replace <token> with your Personal Access Token (PAT) - find this in your ADO settings
orgURL = 'https://analytics.dev.azure.com/<organisation>/' #Replace <organisation with your organisation name

class Authenticate:
    def __init__(self, patToken, orgURL):
        self.patToken = patToken
        self.orgURL = orgURL
    
    def connectToADO(self):
        credentials = BasicAuthentication('', self.patToken) #the space is for the username, but it's not needed with PAT
        connection = Connection(base_url=self.orgURL, creds=credentials)
        return connection
    
    def getCoreClient(self, connection): #Create a client that gets access to projects and data within them
        coreClient = connection.clients.get_core_client() #this method gets the client for us to search with
        return coreClient
    
class Projects(Authenticate):
    def __init__(self, patToken, orgURL):
        super().__init__(patToken, orgURL) #Inherit from auth class

    def getProjectList(self, coreClient): #Get the project list
        projects = coreClient.get_projects()
        projectList = list(projects) #this method returns the projects
        return projectList 
    
    def getWorkItems(self, projectList, connection):
        witClient = connection.clients.get_work_item_tracking_client() #this is our work item searcher client
        workItemList = []
        #wiql query to get work items (wiql is a proprietary SQL-based language)
        for project in projectList:
            wiqlQuery = Wiql(query=f"SELECT * FROM workitems WHERE [System.TeamProject] = '{project.name}' AND [System.WorkItemType] = 'Bug'")
            workItems = witClient.query_by_wiql(wiqlQuery) #make a query to get all work items for a project
            itemIDList = [item.id for item in workItems.work_items]
            for item in range(0, len(itemIDList), 200): #get work items in the max batch size of 200
                idBatch = itemIDList[item:item+200] #batch up work items in groups of 200
                try:
                    workItemsBatch = witClient.get_work_items(idBatch) #get item info from our batches
                    workItemList.extend(workItemsBatch) # add the info to our original list
                except AzureDevOpsClientRequestError:
                    print(f"Error getting work items in batch: {idBatch}")
        return workItemList
    

class DataFrame:
    def __init__(self, workItemList):
        self.workItemList = workItemList
        self.df = pd.DataFrame()

    def createDataframe(self):
        self.workItemList = [item.__dict__ for item in self.workItemList] #convert work items to dictionary
        self.df = pd.json_normalize(self.workItemList) #normalise dict into a dataframe 
        return self.df

    def renameAndCutFields(self):
        renameFields = {'id': "Work Item ID",
                        "fields.System.AreaPath": "Area Path",
                        "fields.System.IterationPath": "Iteration Path",
                        "fields.System.WorkItemType": "Work Item Type",
                        "fields.System.State": "State",
                        "fields.System.AssignedTo.displayName": "Assigned To (Name)",
                        "fields.System.AssignedTo.uniqueName": "Assigned To (Email)",
                        "fields.System.CreatedDate": "Created Date",
                        "fields.System.CreatedBy.displayName": "Created By (Name)",
                        "fields.System.CreatedBy.uniqueName": "Created By (Email)",
                        "fields.System.ChangedDate": "Changed Date",
                        "fields.System.TeamProject": "Client",
                        "fields.System.ChangedBy.displayName": "Changed By (Name)",
                        "fields.System.ChangedBy.uniqueName": "Changed By (Email)",
                        "fields.System.Title": "Title",
                        "fields.Microsoft.VSTS.Common.ClosedBy.uniqueName": "Closed By (Email)",
                        "fields.Microsoft.VSTS.Common.AcceptanceCriteria": "Acceptance Criteria",
                        "fields.System.Tags": "Tags",
                        "fields.System.AssignedTo.inactive": "Assigned To Populated?",
                        "fields.Microsoft.VSTS.Scheduling.RemainingWork": "Remaining Work",
                        "fields.Microsoft.VSTS.Common.Priority": "Priority",
                        "fields.Microsoft.VSTS.Scheduling.CompletedWork": "Completed Work",
                        "fields.Microsoft.VSTS.Scheduling.OriginalEstimate": "Original Estimate",
                        }       

        for column in self.df.columns:
            if column not in renameFields.keys():
                self.df = self.df.drop(column, axis=1)

        self.df = self.df.rename(columns=renameFields)
        return self.df

    def fillEmptyFields(self):
        self.df = self.df.fillna('None')
        return self.df
    
    def changeTypes(self):
        self.df['Created Date'].astype('datetime64', inplace=True)
        self.df['Changed Date'].astype('datetime64', inplace=True)
        return self.df


projectsInstance = Projects(patToken, orgURL)
connection = projectsInstance.connectToADO()
core_client = projectsInstance.getCoreClient(connection)
projects = projectsInstance.getProjectList(core_client)
workItemList = projectsInstance.getWorkItems(projects, connection)

dfInstance = DataFrame(workItemList)
df = dfInstance.createDataframe()
df = dfInstance.renameAndCutFields()
df = dfInstance.fillEmptyFields()
