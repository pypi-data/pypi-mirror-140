Install your own dev instance
=============================

#### Start in debug mode

For debug or for development only, you can launch dgenies through flask in webserver mode:

    dgenies run -m webserver -d

Optional parameters:

`-d` run in debug mode
`-o <IP>` specify the host into run the application (default: 127.0.0.1, set 0.0.0.0 for distant access)
`-p <port>` run in a specified port (default: 5000)
`--no-crons` don't run the crons automatically
`--no-browser` don't start the browser automatically (always true if *-d* option is given)