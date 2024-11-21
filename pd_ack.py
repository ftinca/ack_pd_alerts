import os
import time
import threading
from pdpyras import APISession #pip3 install pdpyras
import sys
import time
sys.argv.append('./')
import pd_db
import re

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def remove_special_chars(input_string):
    return re.sub(r'[^\w\s,\.!?;:\'-]', '', input_string)

def waiting_decorator(func):
    def wrapper(*args, **kwargs):
        def print_dots():
            green = '\033[32m'
            end_clr = '\033[m'
            while not stop_event.is_set():
                for item in [f'{green}.{end_clr} ', f'{green}.{end_clr}:', f'{green}:{end_clr}:',f':{green}.{end_clr}', f' {green}.{end_clr}']:
                    print(f'\r Waiting for incoming alerts {item} ', end='', flush=True)
                    time.sleep(0.3)
        try:
            stop_event = threading.Event()
            thread = threading.Thread(target=print_dots)
            thread.start()
            result = func(*args, **kwargs)
            stop_event.set()
            thread.join()  # Wait for the thread to finish
            return result
        except KeyboardInterrupt:
            show_cursor()
            print('Exiting...')
            pd_db.drop_table()
            stop_event.set()
            thread.join()
            exit(0)
        except Exception as e:
            show_cursor()
            print(f'Error: {e}')
            pd_db.drop_table()
            stop_event.set()
            thread.join()
            exit(1)
    return wrapper

def check_acknowledged_incidents(session):
    check_mark = '\u2713'
    green = '\033[32m'
    end_clr = '\033[m'
    filler = ' ' * 20
    acknowledged_incidents = pd_db.get_acknowledged_incidents()
    for i in acknowledged_incidents:
        pdid, title, _ = i
        incident = session.rget(f'incidents/{pdid}')
        if incident['status'] == 'resolved':
            title = remove_special_chars(title)
            print(f'\r {green}{check_mark}{end_clr} {pdid} - {green}{title}{end_clr}{filler}')
            pd_db.delete_incident_by_id(pdid)
        else:
            pass

def ack(session, incidents):
    warning = '\u26A0'
    yellow = '\033[33m'
    end_clr = '\033[m'
    filler = ' ' * 20
    for i in incidents:
        i['status'] = 'acknowledged'
    updated_incidents = session.rput('incidents', json=incidents)
    for i in updated_incidents:
        title = remove_special_chars(i['title'])
        print(f'\r {yellow}{warning}{end_clr} {i['incident_number']} - {yellow}{title}{end_clr}{filler}')
        pd_db.insert_incident(i['incident_number'], title, i['status'])

def get_triggered_incidents(session, uid):
        pager_duty_incidents = session.list_all(
            'incidents',
            params={'user_ids[]':[uid],'statuses[]':['triggered']}
        )
        return pager_duty_incidents

def get_token_uid():
    token = os.getenv('PD_TOKEN')
    email = os.getenv('PD_MAIL')
    session = APISession(token)
    users = session.list_all('users')
    uid = ''
    for u in users:
        if u['email'] == email:
            uid = u['id']
            break
    if not uid:
        print('User not found.')
        exit(1)
    return session, uid

@waiting_decorator
def main(session, uid):
    while True:
        incident_list = get_triggered_incidents(session, uid)
        if incident_list:
            ack(session, incident_list)
        check_acknowledged_incidents(session)
        time.sleep(3)

if __name__ == '__main__':
    pd_db.init_db()
    hide_cursor()
    session, uid = get_token_uid()
    main(session, uid)
