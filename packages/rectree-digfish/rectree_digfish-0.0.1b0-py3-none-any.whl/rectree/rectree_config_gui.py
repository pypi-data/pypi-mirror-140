# |/usr/bin/env python
import os.path
import PySimpleGUI as sg
import configparser
import socket
import sys

INI_FILENAME = "rectree.ini"


def load_config(ini_file):
    config = configparser.ConfigParser()
    config.read(ini_file)
    return config

def config_gui():
    if len(sys.argv) > 1:
        ini_file = sys.argv[1]
    else: ini_file = INI_FILENAME
    config = load_config(ini_file)
    def_config = config['DEFAULT']
    dir1 = config['dropbox']
    #    print(def_config['icon'])

    #sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)
    layout = [
        [sg.Text('Polling time'), sg.Spin(values=list(range(1,30)),initial_value=int(def_config['wait']), size=(5, 1), key='wait', enable_events=True),
        sg.Text('Icon'),sg.Input(def_config['icon'], size=(25, 1), key='icon'), sg.FileBrowse()]
    ]

    sections = config.sections()

    col1_layout = [  [sg.Button("-",k='remove_direntry_button'), sg.Button('+',k='add_direntry_button')] ,  [ sg.vtop(sg.Listbox([section  for section in sections],key = 'select_direntry',
                    default_values=[sections[0]],size=(0,len(sections)),auto_size_text=True,enable_events=True)) ]]

    col2_layout = [
                    [sg.VPush()],
                    [sg.Text("dir"), sg.Input('Select one item on the left', k='dirname', size=(25, 1), enable_events=True), sg.FolderBrowse(k='dirbrowse',enable_events=True)],
                    [sg.Text('items'), sg.Spin(values=[str(n) for n in list(range(1,40))],initial_value='Nr. items', k='num_items', size=(5, 1),enable_events=True)],
                    [sg.Text("exclusions"),sg.Input('separate each pattern with |',k='exclusions',size=(30,1),enable_events=True)],
                    [sg.VPush()]
                  ]

    layout.extend([[sg.Col(col1_layout),sg.Col(col2_layout)]])

    layout.append([sg.OK(), sg.Cancel()])

    # sg.popup('event:'+event,values)
    win = sg.Window(__file__ + ' config', layout, size=(500, 180),
                    icon=def_config['icon'], resizable=True)

    while True:
        event, values = win.read()

        new_row_counter = 0
        #sg.popup(event,values)
        if (event == 'OK'):
            config['DEFAULT']['wait'] = str(values['wait'])
            config['DEFAULT']['icon'] = values['icon']
            config.write(open(INI_FILENAME, 'w'))
            break

        # elif event == 'wait':
        #     win['wait'].update(values=values['wait'])

        elif event == 'select_direntry':
            sel_direntry = values['select_direntry'][0]
            #sg.popup('select_direntry',sel_direntry)

            if ( not config.has_section(sel_direntry) ):
                win['dirname'].update("new folder")
                win['num_items'].update("n")
                win['exclusions'].update("Separate patterns with |")
            else:
                sel_section = config[sel_direntry]
                #print(win["dirname"])
                win["dirname"].update(sel_section['dir'])
                if 'num' not in sel_section.keys():
                    sel_section['num'] = '10'
                if 'exclude' not in sel_section.keys():
                    sel_section['exclude'] = 'Enter patterns separated with |'
                win["num_items"].update(sel_section['num'])
                win["exclusions"].update(sel_section['exclude'] if 'exclude' in sel_section.keys() else '')

        elif event == 'add_direntry_button':
            nrcstr = str(new_row_counter)
            select = win['select_direntry']
            cur_values = select.get_list_values()
            cur_values.append('new')
            select.update(values=cur_values)

        elif event == 'remove_direntry_button':
            select = win['select_direntry']
            cur_values = select.get_list_values()
            print('Current selected is',select.get())
            cur_selected = select.get()[0]
            cur_values.remove(cur_selected)
            select.update(values=cur_values)
            config.remove_section(cur_selected)

        elif event == 'dirname':
            direntry_path = win['dirname'].get()
            selected_direntry = win['select_direntry'].get()[0]
            if ( config.has_section( selected_direntry)):
                config[selected_direntry]['dir'] = direntry_path
                print("Updated dir",direntry_path)
            else:
                new_section_name = os.path.basename(direntry_path)
                config.add_section(new_section_name)
                config[new_section_name]['dir'] = direntry_path
                print("add new direntry",new_section_name)
                cur_values = win['select_direntry'].get_list_values()
                idx = cur_values.index(selected_direntry)
                cur_values[idx] = new_section_name
                win['select_direntry'].update(values=cur_values)
                win['select_direntry'].set_value(new_section_name)

        elif event == 'num_items':
            section_name = win['select_direntry'].get()[0]
            print("Num_items changed",values['num_items'])
            config[section_name]['num'] = values['num_items']
            print("Num_items changed",config[section_name]['num'])

        elif event == 'exclusions':
            section_name = win['select_direntry'].get()[0]
            config[section_name]['exclude'] = values['exclusions']
            print("Exclusions changed",config[section_name]['exclude'])

        elif event in [sg.WIN_CLOSED,'Cancel',None]:
            break

    win.close()


if __name__ == '__main__': config_gui()
