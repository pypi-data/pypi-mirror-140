from string import Template
from pi_screencontrol_webthing.app import App
from pi_screencontrol_webthing.screen_webthing import run_server


PACKAGENAME = 'pi_screencontrol_webthing'
ENTRY_POINT = "screen"
DESCRIPTION = "A web connected screen control of Raspberry Pi"


UNIT_TEMPLATE = Template('''
[Unit]
Description=$packagename
After=syslog.target

[Service]
Type=simple
ExecStart=$entrypoint --command listen --verbose $verbose --port $port 
SyslogIdentifier=$packagename
StandardOutput=syslog
StandardError=syslog
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
''')



class Application(App):


    def do_process_command(self, command:str, port: int, verbose: bool, args) -> bool:
        if command == 'listen':
            print("running " + self.packagename + " on port " + str(port))
            run_server(port, self.description)
            return True
        elif args.command == 'register':
            print("register " + self.packagename + " on port " + str(port) + " and starting it")
            unit = UNIT_TEMPLATE.substitute(packagename=self.packagename,
                                            entrypoint=self.entrypoint,
                                            port=port,
                                            verbose=verbose)
            self.unit.register(port, unit)
            return True
        else:
            return False


def main():
    Application(PACKAGENAME, ENTRY_POINT, DESCRIPTION).handle_command()


if __name__ == '__main__':
    main()
