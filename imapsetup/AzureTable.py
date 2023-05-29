from azure.data.tables import TableServiceClient
from datetime import datetime
from azure.data.tables import UpdateMode


class AzureTable():
    def __init__(self,
                 connection_string: str,
                 table_name       :str
                                 
                 ):
        self.connection_string         = connection_string
        self.table_service_client      = TableServiceClient.from_connection_string(self.connection_string)
        self.table_name                = table_name

    def CreateTable(self):
        self.table_service_client.get_table_client(self.table_name).create_table()
        return True
                
    def InsetEntity(self,Entity):
        table_client=self.table_service_client.get_table_client(table_name=self.table_name)
        table_client.create_entity(entity=Entity)
        return True
    
    def SelectEntity(self,filter):
        table_client=self.table_service_client.get_table_client(table_name=self.table_name)
        entities = table_client.query_entities(filter)
        data={}
        for entity in entities:
            for key in entity.keys():
                data.update({key:entity[key]})
        return data
        
    def DeleteEntity(self,partitionkey,rowkey):
        table_client=self.table_service_client.get_table_client(table_name=self.table_name)
        table_client.delete_entity(row_key=rowkey, partition_key=partitionkey)
        return True
    
    def UpdateEntity(self,partitionkey,rowkey,updated_data):
        with self.table_service_client.get_table_client(table_name=self.table_name) as table:
            created = table.get_entity(partition_key=partitionkey, row_key=rowkey)
            created["Comments"] = "New comments"
            for obj in updated_data:
                created[obj]  =updated_data[obj]                        
            table.update_entity(mode=UpdateMode.REPLACE, entity=created)
            return True
