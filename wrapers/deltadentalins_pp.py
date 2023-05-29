
def main(scraped_data):
  scraped_data=scraped_data
  EFTPatients=scraped_data.get("EFTPatients")
  if EFTPatients:
    status_obj={}
    for obj in EFTPatients:
      if obj.get("Status"):
        status_obj=obj.copy()
        EFTPatients.remove(obj)

        break
    scraped_data["Status"]=[status_obj ]    

  PpEobClaimDetail=scraped_data.get("PpEobClaimDetail")
  new_data=[]
  new_data_=[]
  if PpEobClaimDetail:
    for obj in PpEobClaimDetail:
      key =list(obj.keys())[0]
      for data in obj[key]:
        data["Enrollee_ClaimId"]=key
      new_data.append(obj[key])  
  scraped_data["PpEobClaimDetail"]=    new_data_
  for i in new_data:
    for j in i:
      new_data_.append(j)
  return scraped_data
