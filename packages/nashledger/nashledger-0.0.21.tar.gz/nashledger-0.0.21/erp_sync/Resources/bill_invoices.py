from erp_sync.Resources.resource import Resource

class BillInvoices(Resource):

    urls = {}

    def set_company_id(self, company_id):
        super().set_company_id(company_id)
        self._set_urls()
        return self

    def _set_urls(self):

        self.urls = {
            "new": f"/companies/{super().get_company_id()}/invoices",
            "edit": f"/companies/{super().get_company_id()}/invoices",
            "import": f"/companies/{super().get_company_id()}/import_bills",
        }

        super().set_urls(self.urls)

        return self

    def edit(self, ledger_id=None, payload=None, method='PUT', endpoint=None):

        self._set_urls()

        self.urls["edit"] = f'{self.urls["edit"]}/{ledger_id}'

        super().set_urls(self.urls)

        return super().edit(payload, method, endpoint)

    def import_data(self, ledger_id=None, payload=None, method='GET', endpoint=None):
        
        self._set_urls()

        if ledger_id is not None:
            self.urls["import"] = f'{self.urls["import"]}/{ledger_id}'
            super().set_urls(self.urls)

        return super().import_data(payload, method, endpoint)

    def payload(self):

        data = {
            "vendor_id ": "<Enter vendor id>",
            "item_id": "<Enter item id>",
            "amount": "<Enter amount",

            "additional_properties":{
                "help":"Optional or extra parameters go here",
                "bill_number": "<Enter the unique bill number or the system will automatically generate one for you>",
            }
        }

        return data


    def serialize(self, payload = None, operation = None):

        data = {"type": "PurchaseInvoice"}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"
        
        if operation == super().NEW or operation == super().UPDATE:

            additional_properties = payload.get("additional_properties", {})        

            # If client type is ZOHO
            if super().get_client_type() == super().ZOHO:

                if 'vendor_id' in payload.keys():
                    data.update({
                        "vendor_id": payload.get("vendor_id", "")
                    })

                line_items = {}

                if 'item_id' in payload.keys():
                    line_items.update({
                        "item_id": payload.get("item_id", "")
                    })

                if 'amount' in payload.keys():
                    line_items.update({
                        "rate": payload.get("amount", "")
                    })
                
                if 'account_id' in additional_properties.keys():
                    line_items.update({
                        "account_id": additional_properties.get("account_id", "")
                    })
                    additional_properties.pop("account_id")

                # if line_items has data in it
                if bool(line_items):
                    data.update({
                        "line_items": [line_items]
                    })                

                if operation == super().NEW:
                        
                    data["bill_number"] = f'{additional_properties.get("bill_number", super().generate_code())}'

                    if 'bill_number' in additional_properties.keys():
                        additional_properties.pop("bill_number")

            # If client type is Quickbooks Online
            elif super().get_client_type() == super().QBO:

                if 'vendor_id' in payload.keys():
                    data.update({
                        "VendorRef": {
                            "value": payload.get("vendor_id", 0)
                        }
                    })

                line_items = {}

                if 'item_id' in payload.keys():
                    line_items.update({
                        "Id": payload.get("item_id", "")
                    })

                if 'amount' in payload.keys():
                    line_items.update({
                        "Amount": payload.get("amount", 0)
                    })

                # if line_items has data in it
                if bool(line_items):
                    data.update({
                        "Line": [line_items]
                    })

            data.update(additional_properties)

            return data

        elif operation == super().READ:

            payload = super().response()

            data = payload

            # confirms if a single object was read from the database
            if isinstance(payload, dict):
                if 'resource' in payload.keys():
                    data = payload.get("resource", [])
                
            # confirms if a single object was read from the database
            if isinstance(data, dict):
                data = [data]
            
            # confirms if data is a list
            if isinstance(data, list):
                if len(data) > 0:
                    for i in range(len(data)):
                        if 'total_amount' in data[i].keys():
                            data[i]['amount'] = data[i].pop('total_amount')
                        if 'customer_id' in data[i].keys():
                            data[i]['vendor_id'] = data[i].pop('customer_id')
                        
            if 'resource' in payload.keys():
                payload["resource"] = data

            super().set_response(payload)

            return self