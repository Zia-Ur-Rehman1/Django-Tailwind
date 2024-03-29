import csv
from django.db import IntegrityError
from ticket.forms import CsvGenerationForm, UploadForm
from ticket.models import Supplier, Ticket, Customer
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import  redirect, render
import pandas as pd
import numpy as np
from django.db.models import Q
def generateCSV(request):
    if request.method == 'POST':
  
        form = CsvGenerationForm(request.POST)
        if form.is_valid():
            # Process form data, for example, save to the database
            supplier_name = form.cleaned_data['supplier_name']
            customer_name = form.cleaned_data['customer_name']
            start_at = form.cleaned_data['start_at']
            end_at = form.cleaned_data['end_at']
            tickets = Ticket.objects.filter(created_at__gte=start_at, 
                                  created_at__lte=end_at).filter(Q(supplier__name__icontains=supplier_name) 
                                                                | Q(supplier=None)).filter(Q(customer__name__icontains=customer_name)
                                                                                           | Q(customer=None))
            if tickets:
                return generate_csv(tickets)
            else:
                messages.warning(request, 'No matching tickets found.')
                return redirect('index')
        else:
            return redirect('index')

def generate_csv(tickets):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tickets_new.csv"'
    csv_writer = csv.writer(response)
    csv_writer.writerow(['Date', 'Passenger Name', 'Sector', 'PNR/V#', 'Supplier', 'Customer', 'Air Line', 'Travel Date', 'Sale', 'Purchase'])
    for ticket in tickets:
        csv_writer.writerow([
            ticket.created_at.strftime('%d-%b') if ticket.created_at else '',
            ticket.passenger if ticket.passenger else '',
            ticket.sector,
            ticket.pnr,
            ticket.supplier.name if ticket.supplier else '',
            ticket.customer.name if ticket.customer else '',
            ticket.airline if ticket.airline else '',
            ticket.travel_date.strftime('%d-%b') if ticket.travel_date else 'Void',
            ticket.sale if ticket.sale else '',
            ticket.purchase if ticket.purchase else '',
        ])

    return response
def process_main_list(df):
    ticket_objects = []
    for index,row in df.iterrows():
        current_date = row['DATE']
        pnr ='' if pd.isna(str(row['PNR/V#'])) else str(row['PNR/V#'])
        sector ='' if pd.isna(str(row['SECTOR'])) else str(row['SECTOR'])
        passenger ='' if pd.isna(str(row['PASSENGER NAME'])) else str(row['PASSENGER NAME'])
        travel_date =None if pd.isna(row['TRAVEL DATE']) else row['TRAVEL DATE']  
        return_date =None if pd.isna(row['RETURN DATE']) else row['RETURN DATE']  
        airline ='' if pd.isna(str(row['AIR LINE'])) else str(row['AIR LINE'])
        sale = int(row['DEAL'])
        purchase = int(row['PURCHASE'])

    # Get or create the Supplier and Customer objects
        supplier, _ = Supplier.objects.get_or_create(name=row['SUPPLIER'])
        customer, _ = Customer.objects.get_or_create(name=row['CUSTOMER'])

        ticket_data = {
            'pnr': pnr,
            'created_at': current_date,
            'sector': sector,
            'passenger': passenger,
            'travel_date': travel_date,
            'return_date': return_date,
            'airline': airline,
            'supplier': supplier,
            'customer': customer,
            'sale': sale,
            'purchase': purchase,
        }
        ticket_objects.append(Ticket(**ticket_data))
    try:
        Ticket.objects.bulk_create(ticket_objects, ignore_conflicts=True)
    except IntegrityError:
        print("IntegrityError occurred during bulk creation.")

    # If the ticket already exists, update its values
def upload_csv(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            print('File Uploaded and is processing.....')
            df = choudry_travels_csv(file)
            print('File Processed Move to Model Processing.....')
            
            missing, mismatched = ticket_model(df)
            selected = ['PNR', 'Balance']
            missing = missing[selected].dropna(ignore_index=True,inplace=False)
            selected_columns = ['PNR', 'purchase', 'Balance']
            mismatched= mismatched[selected_columns]
            mismatched = mismatched.dropna(ignore_index=True)
            response_data = {
                "missing": missing,
                "mismatched": mismatched,
            }
            return render(request, "upload.html", response_data)
    else:
        form = UploadForm()
    return render(request, "upload.html", {"form": form})

def hasnain_travels_mainlist_csv(file):
    df= pd.read_csv(file, skiprows=2, usecols=list(range(12))).dropna(how='all')
    df =df.replace(np.nan, '')
    df['PURCHASE'] = pd.to_numeric(df['PURCHASE'].str.replace(',', ''), errors='coerce').fillna(0).astype(int)
    df['DEAL'] = pd.to_numeric(df['DEAL'].str.replace(',', ''), errors='coerce').fillna(0).astype(int)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
# df.rename(columns={'N.CHOUDHARY TICKETS': 'Purchase'}, inplace=True)
    current_year = pd.Timestamp.now().year
    date_format = "%Y-%m-%d"
    df['DATE'] = pd.to_datetime(df['DATE'] + '-' + str(current_year), errors='coerce')
    df['TRAVEL DATE'] = df['TRAVEL DATE'].replace({'VOID': '','void': ''})
    split_dates = df['TRAVEL DATE'].str.split('/', expand=True)
    df['TRAVEL DATE'] = split_dates[0]
    df['RETURN DATE'] = split_dates[1]
    df['TRAVEL DATE'] = pd.to_datetime(df['TRAVEL DATE'] + '-' + str(current_year), format=date_format, errors='coerce')
    df['RETURN DATE'] = pd.to_datetime(df['RETURN DATE'] + '-' + str(current_year), format=date_format, errors='coerce')
    return df

    
def choudry_travels_csv(file):
    df2= pd.read_csv(file, skiprows=4).dropna(how='all')
    df2['PNR'] = df2['Narration'].apply(lambda x: (x.split('-')[3].strip() if pd.notna(x) and 'VISA VOUCHER' not in x and len(x.split('-')) >= 4 else None) or (x.split('-')[-1].strip() if pd.notna(x) and 'VISA VOUCHER' in x else None))
    df2['Debit'] = pd.to_numeric(df2['Debit'].str.replace(',', ''), errors='coerce').fillna(0).astype(float)
    df2['Credit'] = pd.to_numeric(df2['Credit'].str.replace(',', ''), errors='coerce').fillna(0).astype(float)
    df2.drop('Narration', axis=1, inplace=True)
    df2['PNR'] = df2['PNR'].str.strip()
    result_df2 = df2.groupby('PNR', as_index=False).agg({'Debit': 'sum', 'Credit': 'sum'})
    result_df2['Balance'] = result_df2['Debit'] - result_df2['Credit']
    result_df2['PNR'] = result_df2['PNR'].str.strip()
    # result_df2 = result_df2[['PNR', 'Balance']]
    return result_df2
def ticket_model(df):
    model_data = Ticket.objects.filter(supplier=3).values('pnr', 'purchase')
    print('Got Model Data.....')
    print('Comparing with Choudry Travels.....')
    model_df = pd.DataFrame.from_records(model_data)
    model_df.rename(columns={'pnr': 'PNR'}, inplace=True)
    result_df = model_df.groupby('PNR', as_index=False)['purchase'].sum()
    print('Merging with Choudry Travels.....')
    
    merged_df = pd.merge(result_df, df, on='PNR')
    missing_pnr_df = df[~df['PNR'].isin(merged_df['PNR'])]
    print('Getting Mismatches.....')
    
    matched_rows = merged_df[merged_df['PNR'] == merged_df['PNR']]
    print('Getting matches.....')
    matched_rows['purchase'] = pd.to_numeric(matched_rows['purchase'], errors='coerce')
    matched_rows['Balance'] = pd.to_numeric(matched_rows['Balance'], errors='coerce')
    mismatched_rows = matched_rows[abs(matched_rows['purchase'] - matched_rows['Balance']) > 5]
    
    # merged_df['difference'] = merged_df['purchase'] - merged_df['Balance']
    return missing_pnr_df, mismatched_rows
def compare_csv(HT,CT):
    result_df = df.groupby('PNR')['Purchase'].sum().reset_index()
    
    merged_df = result_df.merge(result_df2, left_on='PNR', right_on='PNR', how='inner')
    matched_rows = merged_df[merged_df['PNR'] == merged_df['PNR']]
    matched_rows['Purchase'] = pd.to_numeric(matched_rows['Purchase'], errors='coerce')
    matched_rows['Balance'] = pd.to_numeric(matched_rows['Balance'], errors='coerce')
    mismatched_rows = matched_rows[abs(matched_rows['Purchase'] - matched_rows['Balance']) > 5]
    mismatched_data = mismatched_rows[['PNR', 'Purchase', 'Balance']]
    mismatched_data.to_csv('mismatched_data.csv', index=False)
    
def compare_pnr(HT,CT):
    merged_result = pd.merge(result_df, result_df2, on='PNR', how='right', indicator=True)

    missing_pnr_result_df2 = merged_result[merged_result['_merge'] == 'right_only'][result_df2.columns]
    missing_pnr_result_df2.to_csv('missing_pnr_result_df2.csv', index=False)

def process_name(name):
    parts = name.replace('MR', '').replace('MRS', '').split()
    if len(parts) == 2:
        return ' '.join(parts[::-1])
    elif len(parts) == 3:
        return ' '.join(parts[-2:][::-1] + [parts[0]])
    else:
        return name
    
def travel_point():
    df2= pd.read_csv('TP.csv', skiprows=12).dropna(how='all')
    df2['Ticket No.']= df2['Ticket No.'].dropna()
    df2['Ticket No.']= df2['Ticket No.'].iloc[:54]
# def travel_point(file):
# df = pd.read_csv('TP.csv', skipinitialspace=True, usecols=[2,6], skiprows=1).dropna(how='all')
# df = df[df['TRAVEL POINT TICKETS'].notna()]
# df2 = pd.read_csv('TP2.csv', skipinitialspace=True, usecols=[2,6], skiprows=1).dropna(how='all')
# df2 = df2[df2['TRAVEL POINT TICKETS'].notna()]
# result_df = pd.concat([df, df2], ignore_index=True)
# result_df.rename(columns={'TRAVEL POINT TICKETS': 'Purchase'}, inplace=True)
# result_df.rename(columns={'pax': 'Passenger'}, inplace=True)
# result_df = result_df[~result_df['Passenger'].str.contains('BALANCE')]
# result_df['Purchase'] = pd.to_numeric(result_df['Purchase'], errors='coerce').abs()

# df3 = pd.read_csv('TPorg.csv', skipinitialspace=True, usecols=[4,10], skiprows=12).dropna(how='all')
# df3 = df3.dropna()
# end_df = pd.concat([result_df, df3], axis=1)

# print(f"HT: {result_df.to_string()} TP:  {df3.to_string()}")
# df3['Passenger'] = df['Passenger'].apply(process_name)

