from colorama import Fore


def check_rate_con_data(rate_con):
    try:
        data_check_passed = True
        if type(rate_con['shipment']) != dict:
            data_check_passed = False

        if type(rate_con['receiver']) != dict:
            data_check_passed = False

        if type(rate_con['sender']) != str:
            data_check_passed = False

        if type(rate_con['client']) != str:
            data_check_passed = False

        if type(rate_con['stops']) == list:
            if len(rate_con['stops']) > 0:
                for stop in rate_con['stops']:
                    if type(stop['_stoptype']) != str:
                        data_check_passed = False

                    if type(stop['stoptype']) != str:
                        data_check_passed = False

                    if type(stop['order_detail']) == list:
                        if len(stop['order_detail']) < 1:
                            data_check_passed = False

                    for entity in stop['entities']:
                        if type(entity['name']) != str:
                            data_check_passed = False

                        if type(entity['city']) != str:
                            data_check_passed = False

                        if type(entity['state']) != str:
                            data_check_passed = False

                        if type(entity['postal']) != str:
                            data_check_passed = False

        if data_check_passed is True:
            print(Fore.GREEN + f"[PASSED][ALL-DATA-CHECK]" + Fore.BLACK)
        else:
            print(Fore.RED + f"[FAILED][DATA-CHECK]" + Fore.BLACK)
    except Exception as e:
        data_check_passed = False
        print(Fore.RED + f"[FAILED][RateCon-DataCheck-Error][{e}][{Exception}]" + Fore.BLACK)
        return data_check_passed
