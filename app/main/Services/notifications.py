import time
import smtplib
import pprint

from app import mail_user, mail_password, smtp_server_string, port

pp = pprint.PrettyPrinter(indent=4)

def send_tank_alert_mail(to_emails, tanks_parameters, current_tank_values):
    string_alert_list = []

    print("-------TO MAILS------------------")
    print(to_emails)
    print("---------------TANKS PARAMETERS--------------")
    pp.pprint(tanks_parameters)
    print("--------------CURRENT TANK VALUES----------------")
    pp.pprint(current_tank_values)

    for current_tank_value in current_tank_values:
        tank_parameter = [tank_parameter for tank_parameter in tanks_parameters if current_tank_value['id'] == tank_parameter['tank_name']]
        tank_value_selected = tank_parameter[0]
        print("CURRENT TANK VALUE EVALUATED")
        print(current_tank_value)
        print("TANK PARAMETER SELECTED")
        print(tank_value_selected)

        if float(current_tank_value['wtrLvlValue']) > float(tank_value_selected['WtrLvl']['tank_max_value']):
            string_alert_list.append(f"Tank ID {current_tank_value['id']} water level value surpassed top boundary with {current_tank_value['wtrLvlValue']} having as limit {tank_value_selected['WtrLvl']['tank_max_value']}")
        if float(current_tank_value['wtrLvlValue']) < float(tank_value_selected['WtrLvl']['tank_min_value']):
            string_alert_list.append(f"Tank ID {current_tank_value['id']} water level value is below smallest boundary with {current_tank_value['wtrLvlValue']} having as limit {tank_value_selected['WtrLvl']['tank_min_value']}")
        
        if float(current_tank_value['oxygenPercentageValue']) > float(tank_value_selected['OxygenPercentage']['tank_max_value']):
            string_alert_list.append(f"Tank ID {current_tank_value['id']} %Oxygen value surpassed top boundary with {current_tank_value['oxygenPercentageValue']} having as limit {tank_value_selected['OxygenPercentage']['tank_max_value']}")
        if float(current_tank_value['oxygenPercentageValue']) < float(tank_value_selected['OxygenPercentage']['tank_min_value']):
            string_alert_list.append(f"Tank ID {current_tank_value['id']} %Oxygen value is below smallest boundary with {current_tank_value['oxygenPercentageValue']} having as limit {tank_value_selected['OxygenPercentage']['tank_min_value']}")

        if float(current_tank_value['phValue']) > float(tank_value_selected['Ph']['tank_max_value']):
            string_alert_list.append(f"Tank ID {current_tank_value['id']} Ph value surpassed top boundary with {current_tank_value['phValue']} having as limit {tank_value_selected['Ph']['tank_max_value']}")
        if float(current_tank_value['phValue']) < float(tank_value_selected['Ph']['tank_min_value']):
            string_alert_list.append(f"Tank ID {current_tank_value['id']} Ph value is below smallest boundary with {current_tank_value['phValue']} having as limit {tank_value_selected['Ph']['tank_min_value']}")
    
    """for tank_parameters in tanks_parameters:
        tank_current_index = current_tank_values['id'].index(tank_parameters['tank_name'])
        measure_type = tank_parameters['measure_type']
        parameter_min_value = tank_parameters['tank_min_value']
        parameter_max_value = tank_parameters['tank_max_value']

        current_value = current_tank_values[measure_type][tank_current_index]
        if current_value < parameter_min_value:
            string_alert_list.append(f"Tank {tank_parameters['tank_name']} is less than inferior category {measure_type} with current value of {current_value} bound value {parameter_min_value} at {time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(current_tank_values['timestamp'][tank_current_index]))}\n")
        elif current_value > parameter_max_value:
            string_alert_list.append(f"Tank {tank_parameters['tank_name']} is greater than superior category {measure_type} with current value of {current_value} bound value {parameter_max_value} at {time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(current_tank_values['timestamp'][tank_current_index]))}\n")"""
        
    print("---------PRINTING STRING MESSAGES------------")
    print(string_alert_list)
    print("----------PRINTING LENGTH MESSAGES--------------")
    print(len(string_alert_list))

    if len(string_alert_list):
        sent_from = mail_user
        to = to_emails
        subject = 'TANKS ALERT MESSAGE: BOUNDS SURPASSED! - SUMMARY'
        body = "\n".join(string_alert_list)
        print("---------PRINTING MAIL BODY--------------")
        print(body)
        email_text = """\
        From: %s
        To: %s
        Subject: %s

        %s
        """ % (sent_from, ", ".join(to), subject, body)

        try:
            send_email(to, "TANK EMAIL ALERTS", email_text)
            print ("Email sent successfully!")
        except Exception as ex:
            print ("Something went wrong….",ex)
    print("AFTER SENDING EMAILS !!!")

def send_email(to_emails, subject, body):
    gmail_user = mail_user
    gmail_password = mail_password

    sent_from = gmail_user
    to = to_emails
    subject = subject
    body = body
    print("---------PRINTING MAIL BODY--------------")
    print(body)
    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        smtp_server = smtplib.SMTP_SSL(smtp_server_string, port)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        print ("Email sent successfully!")
    except Exception as ex:
        print ("Something went wrong….",ex)