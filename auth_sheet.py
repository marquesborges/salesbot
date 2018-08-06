from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CREDENTIAL = 'credentials.json'
SPREADSHEET_ID = '1lnahdxJwAGD5tEmQ00zui1DJD6Sdw7Zb7dzd0sDXA_4'
RANGE = "!A1:H"
RANGE_ITEM = "!A2:H"


class SheetGoogle(object):

    def __init__(self):
        super(SheetGoogle, self).__init__()

        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(CREDENTIAL, SCOPES)
            creds = tools.run_flow(flow, store)

        self.service = build('sheets', 'v4', http=creds.authorize(Http()))
        self.spreadsheet = dict()
        self.sheet = {"sheet_id": None,
            "title": None,
            "values": []}

    def __enter__(self):
        return self.service.spreadsheets()

    def __exit__(self, type, value, traceback):
        pass

    def load_spreadsheet(self, *args):
        try:
            with SheetGoogle() as spreadsheet:
                request = spreadsheet.get(spreadsheetId=SPREADSHEET_ID)
                self.spreadsheet = request.execute()
        except Exception as e:
            raise Exception("Erro na leitura da Planilha: {}".format(e))

    def load_sheet(self, sheet_name):
        try:
            self.load_spreadsheet()
            all_sheets = self.spreadsheet["sheets"]
            sheet_list = list(filter(
                lambda s: s["properties"]["title"] == sheet_name,
                all_sheets))
            if (len(sheet_list) > 0):
                self.sheet["sheet_id"] = sheet_list[0]["properties"]["sheetId"]
                self.sheet["title"] = sheet_list[0]["properties"]["title"]
        except Exception as e:
            raise Exception("Erro na leitura da Aba {}: {}".format(sheet_name,
            e))

    def sheet_values(self, sheet_name):
        try:
            self.load_sheet(sheet_name)
            with SheetGoogle() as spreadsheet:
                range_ = self.sheet["title"] + RANGE_ITEM
                request = spreadsheet.values().get(
                    spreadsheetId=SPREADSHEET_ID,
                    range=range_,
                    majorDimension="ROWS")
                response = request.execute()
                self.sheet["values"].append(response.get("values", []))
        except Exception as e:
            raise Exception("Erro ao obter valores da Aba {}: {}".format(
                sheet_name,
                e))

    def add_sheet_values(self, *args, **kwargs):
        try:
            sheet_name = args[0]
            self.load_sheet(sheet_name)
            sheet_exists = (self.sheet["sheet_id"] is not None)

            if (not sheet_exists):
                self.add_new_sheet(sheet_name)

            with SheetGoogle() as spreadsheet:
                range_ = self.sheet["title"] + RANGE
                data = {"range": range_,
                    "majorDimension": "ROWS",
                    "values": []}

                data["values"].append(kwargs["hdr"])
                data["values"].append(kwargs["title"])

                for line in kwargs["line"]:
                    data["values"].append(line)

                data["values"].append(kwargs["foot"])
                request = spreadsheet.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    valueInputOption="USER_ENTERED",
                    #insertDataOption="INSERT_ROWS",
                    includeValuesInResponse=True,
                    range=range_,
                    body=data)
                response = request.execute()["updatedData"]

                self.sheet["values"].append(response.get("values", []))
        except Exception as e:
            raise Exception("Erro ao enviar valores para a Aba {}: {}".format(
                sheet_name,
                e))

    def add_new_sheet(self, sheet_name):
        try:
            with SheetGoogle() as spreadsheet:
                sheet = {"properties": {"title": sheet_name,
                "sheetType": "GRID"}}
                request_body = {"requests": [{"addSheet": sheet}]}
                request = spreadsheet.batchUpdate(spreadsheetId=SPREADSHEET_ID,
                    body=request_body)

                response = request.execute()["replies"][0]["addSheet"]
                self.sheet["sheet_id"] = response["properties"]["sheetId"]
                self.sheet["title"] = response["properties"]["title"]
        except Exception as e:
            raise Exception("Erro adcionar a nova Aba {}: {}".format(
                sheet_name,
                e))
