import json

eftpatients = { "MemberNo","PatientName","PayerClaimId","PayerPaid","PlanType","PPTransPayorListID","ProviderClaimId","RecordID","RenderingProviderFirstName","RenderingProviderID","RenderingProviderLastName","SubscriberID"}
eobclaimmaster = {'ClaimStatus','EFT_CheckNumber','Notes','PayeeAddress','PayeeCity','PayeeName','PayeeState','PayeeTaxID','PayeeZip','PayerAddress','PayerCity','PayerClaimID','PayerContact','PayerID','PayerName','PayerState','PayerZip','PaymentMethodCode','PPGridViewId','PPTransPayorListID','RecordID','RenderingProvider','RenderingProviderID','SubscriberID','TotalAmount','url'}
eobclaimdetails = {"ActualAllowed","Adjustments","ContractualObligations","Enrollee_ClaimID","OtherAdjustments","PatientResp","PayableAmount","PayerInitiatedReductions","ProcCode","RecordID","RemarkCodes","ServiceDate","SubmittedCharges","PPGridViewId"}

file_path = "C:\\guardian\\SD%20Payor%20Scraping\\guardian_output.json"
with open(file_path, "r") as file:
    data = json.load(file)


eftpatientsoutput = set(data['EFTPatients'][0].keys())
eobclaimmasteroutput = set(data['PpEobClaimMaster'][0].keys())
eobclaimdetailoutput = set(data['PpEobClaimDetail'][0].keys())
print("\n")
print("EFTAPatients", eftpatients - eftpatientsoutput)
print("EobClaimMaster", eobclaimmaster - eobclaimmasteroutput)
print("EobClaimdetail", eobclaimdetails - eobclaimdetailoutput)