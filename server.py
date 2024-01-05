import sys;
from http.server import HTTPServer, BaseHTTPRequestHandler;
from MolDisplay import Molecule;
import molecule;  #do i import this
from urllib.parse import urlparse, parse_qs;
import io;
from io import BytesIO
from molsql import Database;
import re;

webPage = {
            "/": "index.html",
            "/update.html": "update.html",
            "/upload.html": "upload.html",
            "/list.html": "list.html",
            "/display.html": "display.html", 
            "/index.html": "index.html",
            "/main.css":"main.css", 
            "/main.js":"main.js"
        }

class MyHandler(BaseHTTPRequestHandler):
    # presents web-form
    def do_GET(self):
        # print("PATH: ", self.path)
        if self.path in webPage:
            self.send_response( 200 ); # OK
            # Send and submit the form
            self.send_header( "Content-type", "text/html" );
            with open(webPage[self.path], "r") as fileContents:
                html = fileContents.read()
            fileContents.close()
            
            self.send_header( "Content-length", len(html) );
            self.end_headers();
            self.wfile.write( bytes( html, "utf-8" ) );

        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );

    # Sends svg file to cilent
    def do_POST(self):
        print("PATH:", self.path)
        if self.path == "/molecule":  #fix 
            contentType = self.headers.get("Content-Type", "")
            contentLength = int(self.headers.get("Content-Length", "0"))
            
            # Acesss the uploaded file
            content = self.rfile.read(contentLength)

            # Convert it to Bytes, then to textIO
            contentIO = io.TextIOWrapper(io.BytesIO(content))

            for i in range(0,4):
                string = next(contentIO);

            findName = 'name="NAME"\r\n\r\n(\w+)'
            flag = re.search(findName, content.decode('utf-8'))
            if flag:
                molName = flag.group(1)

            mol = Molecule();

            # Create instance of molecule
            sq = Database()
            uniqueMol = sq.uniqueMolecule(molName)
            if(uniqueMol == 0):

                sq.add_molecule(molName,contentIO);
                message = "sdf file uploaded to database";

            else:
                message = "sdf file was not uploaded to database. Duplicate molecule";

            # Send response back to display molecule
            
            self.send_response( 200 ); # OK
            '''
            self.send_header('Content-type', 'text/html')
            with open("upload.html", "r") as fileContents:
                html = fileContents.read()
            fileContents.close()
            self.send_header( "Content-length", len(html) );
            self.end_headers();
            self.wfile.write( bytes( html, "utf-8" ) );
            '''
            self.nagivateWebPage("upload.html")
            self.wfile.write(f'<script>alert("{message}");</script>'.encode('utf-8'))

        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );
    
    def nagivateWebPage(self, pageName):
        self.send_header('Content-type', 'text/html')
        with open(pageName, "r") as fileContents:
                html = fileContents.read()
        fileContents.close()
        self.send_header( "Content-length", len(html) );
        self.end_headers();
        self.wfile.write( bytes( html, "utf-8" ) );


        



'''
# webform that is presented by do_GET
form = """
<html>
    <head>
    <title> File Upload </title>
    </head>
    <body>
        <h1> File Upload </h1>
        <form action="molecule" enctype="multipart/form-data" method="post">
            <p>
                <input type="file" id="sdf_file" name="filename"/>
            </p>
            <p>
                <label for="NAME">Molecule Name:</label><br>
                <input type="text" id="NAME" name="NAME"><br>
            </p>
            <p>
                <input type="submit" value="Upload"/>
            </p>
        </form>
    </body>
</html>
""";
'''

httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler );

httpd.serve_forever();
