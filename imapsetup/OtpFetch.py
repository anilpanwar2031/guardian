from AzureTable import AzureTable
from time import sleep
import os

# otptable =AzureTable(con,tablename)


def InsertTable(state,website,email_id,otptable):
    otptable.InsetEntity({
        u'PartitionKey': website,
        u'RowKey':email_id,
        u'Status': state,
        u'Email':email_id
        })

def AddOtp(website,email_id,otptable):
    data =otptable.SelectEntity(f"PartitionKey eq '{website}' and Email eq '{email_id}' and Status eq 'Pending'")

    print(len(data))
    if len(data)   == 0:
        InsertTable("Pending",website,email_id,otptable)
        return True
        #data =otptable.SelectEntity("Status eq 'Pending'")
    else:
        print("Email Pending in queue")
        return False

def DeleteOtp(website,email_id,otptable):
    otptable.DeleteEntity(website,email_id)
    return True
def update_status(website,email_id,status,otptable):
    otptable.UpdateEntity(website,email_id,{"Status":status})



def OtpFetch(website,email_id,OtpHandler):
    con              =       os.environ['ConnectionString']
    tablename        =       os.environ['IMAPTableName']
    otptable =AzureTable(con,tablename)    
    limit =0
    while True:
        is_job=AddOtp(website,email_id,otptable) 
        if is_job:
            final_otp  =OtpHandler.otp_fetch_with_imap()
            DeleteOtp(website,email_id,otptable)
            print(final_otp)           
            return final_otp            
        else:
            sleep(10)
            limit+=10
            if limit ==300:
                DeleteOtp(website,email_id,otptable)
                return None   

        
            