import pandas as pd

""" 
Read google sheet as dataframe
Usage example: read_gsheet("https://sheet.google.com/45qwd3533")
"""


def read_gsheet(url, credentials = None, sheet = None):

    if credentials != True:

        gc = gspread.service_account(credentials)

        if sheet != None:

            wks = gc.open_by_url(url).worksheet(sheet)

        else:

            wks = gc.open_by_url(url).get_worksheet(0)


        data = wks.get_values(value_render_option='UNFORMATTED_VALUE', date_time_render_option = "FORMATTED_STRING")

        headers = data.pop(0)

        df = pd.DataFrame(data, columns = headers)


    #else: 

        #df = ##chiamata API

    return df


""" 
Read hubspot contacts as dataframe
Usage example: read_hubspot_contacts(api_key)
"""


def read_hubspot_contacts(api_key, offset=100):
    from askdata.integrations import hubspot
    return hubspot.get_contacts_df(api_key, offset)


""" 
Read alpha vantage api
Usage example: read_alphavantage_stock(api_key, symbols)
"""


def read_alphavantage_stock(symbols, api_key):
    from askdata.integrations import alphavantage
    return alphavantage.get_daily_adjusted_df(symbols, api_key)


def normalize_columns(df: pd.DataFrame):
    problematicChars = [",", ";", ":", "{", "}", "(", ")", "=", ">", "<", "."]
    new_cols = {}
    for column in df.columns:

        columnName = column.lower()

        for p_char in problematicChars:
            columnName = columnName.replace(p_char, "")

        columnName = columnName.replace(" ", "_")
        columnName = columnName.replace("-", "_")
        columnName = columnName.strip()

        for p_char in problematicChars:
            columnName = columnName.replace(p_char, "")

        new_cols[column] = columnName

    return df.rename(columns=new_cols)


def read(type, settings):
    if type == "CSV":
        return __read_csv(settings)
    if type == "EXCEL":
        return __read_excel(settings)
    if type == "PARQUET":
        return __read_parquet(settings)
    if type == "GSHEET":
        return __read_gsheet(settings)
    if type == "Hubspot":
        return __read_hubspot(settings)
    else:
        raise TypeError("Dataset type not supported yet")


def __read_csv(settings: dict):
    
    # Handle thousands
    if settings["thousands"] == "None":
       settings["thousands"] = None

    # Read source file
    df = pd.read_csv(filepath_or_buffer=settings["path"], sep=settings["separator"], encoding=settings["encoding"], thousands=settings["thousands"])

    # Detect if any column is a date-time
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                pass

    # Exec custom post-processing
    if "processing" in settings and settings["processing"] != "" and settings["processing"] != None:
        exec(settings["processing"])

    return df

def __read_parquet(settings: dict):
    
    df = pd.read_parquet(path=settings["path"])

    return df

def __read_excel(settings: dict):
    df = pd.read_excel(settings["path"])

    # Detect if any column is a date-time
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                pass

    return df

def __read_gsheet(settings: dict):
    df = read_gsheet(settings["url"])

    return df

def __read_hubspot(settings: dict):
    df = read_hubspot_contacts(settings["fields"]["token"])

    return df




##################################
########## FACEBOOK ADS ##########
##################################


def read_fb_ads(my_app_id, my_app_secret, my_access_token,
                
                date_preset = "last_7d",
                
                account_name = {'Numbers' : 'act_113103090066338',
                                'Linkers' : 'act_203938767415072',
                                'WinWay' : 'act_2591302164494270',
                                'Miss Tariffa Agency' : 'act_280378753012689',
                                'Humable' : 'act_284748836042514',
                                'Miss Tariffa' : 'act_503932150489858',
                                'We are Fiber' : 'act_638714426864395'
                                }):
    
    from askdata.integrations import facebook_api
    
    fb_ads = facebook_api.get_fb_ads(my_app_id, my_app_secret, my_access_token, date_preset, account_name)

    return fb_ads



#################################
########## GOOGLE ADS ##########
################################


def read_google_ads(n_range = 7, 
                   
                  admin_account = {'Be You': '291-824-5921'
                                 ,'Humable': '760-045-3647'
                                 ,'Linkers': '504-714-3560'
                                 ,'Miss Tariffa': '605-298-4997'
                                 ,'Miss Tariffa Agency': '427-886-1215'
                                 ,'Numbers': '794-577-9076'
                                 ,'Wearefiber': '778-681-5313'
                                },
                   
                   yaml_file_path = 'googleads.yaml'):
    
    
    from askdata.integrations import google_api
    
    google_ads = google_api.get_google_ads(n_range, admin_account, yaml_file_path)
    
    return google_ads
    
    
    
    
###################################
########## AIRCALL CALLS ##########
###################################



def read_aircall_calls(token, api_key, #mandatory
                      
                      start = 7, end = 0 #optional
                     ):
    
    from askdata.integrations import aircall_api
    
    aircall_calls = aircall_api.get_aircall_calls(token, api_key, start, end)
    
    return aircall_calls
    
    
    
#############################
########## HUBSPOT ##########
#############################
    

## hubspot deals

def read_hubspot_deals(API_KEY, 
                        
                        #optional input
                        n_days = 7):
    
    
    from askdata.integrations import hubspot_api
    
    deals_all_fiels = hubspot_api.get_hubspot_deals_all_fields(API_KEY, n_days)
    
    return deals_all_fiels
 

    
## hubspot contact

def read_hubspot_contact(API_KEY,
                         
                         #optional input
                         n_days = 7):
    
    from askdata.integrations import hubspot_api
    
    hubspot_contact = hubspot_api.get_hubspot_contact(API_KEY, n_days)
    
    return hubspot_contact
                         
           
        
## hubspot pipelines

def read_hubspot_pipelines(API_KEY):
    
    
    from askdata.integrations import hubspot_api
    
    hubspot_pipelines = hubspot_api.get_hubspot_pipelines(API_KEY)
    
    return hubspot_pipelines
                         
                         
    
## hubspot users

def read_hubspot_users(API_KEY):
    
    from askdata.integrations import hubspot_api
    
    hubspot_users = hubspot_api.get_hubspot_users(API_KEY)
    
    return hubspot_users
    