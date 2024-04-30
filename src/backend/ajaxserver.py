import sys;
from http.server import HTTPServer, BaseHTTPRequestHandler;
from urllib.parse import urlparse, parse_qs;
import io;
from io import BytesIO
import urllib;
import json;

from MolDisplay import Molecule;
from MolDisplay import Atom;
from MolDisplay import Bond;
import MolDisplay;

import molecule;
from molsql import Database;
import re
import sqlite3

class MyHandler(BaseHTTPRequestHandler):
    # presents web-form
    def do_GET(self):
        self.webPage = {
            "/": "index.html",
            "/update.html": "update.html",
            "/upload.html": "upload.html",
            "/list.html": "list.html",
            "/index.html": "index.html",
            "/style.css" : "style.css", 
            "/script.js" : "script.js"
        }
        # Navigate to different web pages 
        if self.path in self.webPage:
            self.send_response( 200 ); # OK
            if(self.path == "/style.css"):
                 self.send_header( "Content-type", "text/css" );
            else:
                self.send_header( "Content-type", "text/html" );
            with open(self.webPage[self.path], "r") as fileContents:
                html = fileContents.read()
            fileContents.close()
            # These pages are dynamic based on database 
            if(self.path == '/update.html'):
                html = self.createElementPage()
            if(self.path == '/list.html'):
                html = self.createListPage()
            
            self.send_header( "Content-length", len(html) );
            self.end_headers();
            self.wfile.write( bytes( html, "utf-8" ) );

        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );

    def do_POST(self):
        global svgContent
        global sentMolName
        # Element Form Adding handling
        if(self.path == "/elementForm"):
            # Read data
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);
            elementDict = urllib.parse.parse_qs( body.decode( 'utf-8' ) );
            formLen = 7
            dictLen = len(elementDict.items())
            formFlag = 0;    
            # Depending on form item it is converted to int
            for key, value in elementDict.items():
                if( (key == "ELEMENT_NO") or (key == "RADIUS")):
                    elementDict[key] = int(value[0])
                elif( (key == "COLOUR2") or (key == "COLOUR1") or (key == "COLOUR3")):
                    
                    elementDict[key] = (value[0][1:].capitalize())
                else:
                    elementDict[key] = value[0]
                    

            elementList = list(elementDict.items())
            uniqueElement = 0

            # Check if element is unique
            if(len(elementList) == 7):
                try:
                    uniqueElement = sq.uniqueElement(elementList[2][1], elementList[1][1])
                except Exception as e:
                    message = "An error occured. Please check input fields."
                    uniqueElement = 1
                    formFlag = 1
            else:
                formFlag = 1
                message = "Please fill in all fields with an appropriate input"
            
            # Add element to table
            if((formFlag == 0) and (uniqueElement == 0)):
                try:
                    sq['Elements'] = (elementList[0][1], elementList[1][1], elementList[2][1], elementList[3][1], elementList[4][1], elementList[5][1], elementList[6][1])
                    message = "Element has been uploaded";
                except Exception as e:
                    message = "An error occured. Please check input fields."

            elif((uniqueElement > 0) and (formFlag == 0)):
                message = "Not uploaded. Please add a unique element. No duplicates"
            else:
                message = "Error. Element not uploaded"
            if(formLen != dictLen):
                formFlag = 1
                message = "Please fill in all the fields of the form"

            self.sendMessage(message)
            
        # Uploading SDF file
        elif(self.path == "/sdfFileForm"):
            # Read data
            contentType = self.headers.get("Content-Type", "")
            contentLength = int(self.headers.get("Content-Length", "0"))
            content = self.rfile.read(contentLength)
            contentIO = io.TextIOWrapper(io.BytesIO(content))

            for i in range(0,4):
                string = next(contentIO);
            svgContent = contentIO
            # Check if file type is correct
            fileFlag = self.correctFilename(content)

            if(fileFlag == 0):
                message = "Uploaded SVG File.";           
            else:
                message = "Incorrect file type. Please upload sdf files";
            
            self.sendMessage(message)
            
        # Molecule name form
        elif(self.path == '/molNameForm'):
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            # print( repr( body.decode('utf-8') ) );

            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );
            molName = postvars['NAME'][0]
            # Check for unique molecule name
            uniqueMol = sq.uniqueMolecule(molName)

            uploadFlag = 0
            # Check if sdf file has been uploaded
            try:
                svgContent
            except NameError:
                uploadFlag = 1
                message = "Please upload sdf file first"
            else:
                uploadFlag = 0

            # add molecule to database
            if((uniqueMol) == 0 and (uploadFlag == 0)):
                try:
                    sq.add_molecule(molName,svgContent);

                    message = "Molecule uploaded to database";
                except Exception as e:
                    message = "An error occured with the file. Please upload an sdf file"
            elif((uniqueMol) == 1 and (uploadFlag == 0)):
                message = "sdf file was not uploaded to database. Duplicate molecule";
            else:
                message = "Please upload sdf file first"
            
            svgContent = None
            
            self.sendMessage(message)
           
        # Delete element form
        elif(self.path == '/elementDelForm'):
            # Read data
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);
            element = body.decode( 'utf-8' )
            element = re.sub(r"^.*?'(.*?)'.*$", r"\1", element)
            # delete element 
            if(len(element) != 0):
                sq.deleteElement(element)
                message = element+" has been deleted"
            else:
                message = "Please select an element"
            self.sendMessage(message)
            
        # Display molecule svg
        elif(self.path == '/moleculeForm'):
            
            # read data
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);
            molecule = body.decode( 'utf-8' )
            molecule = molecule[4:]

            message = molecule + " is displayed"
            sentMolName = molecule
            svgContent = self.displayMolecule(molecule)
            # send molecule SVG
            self.send_response( 200 ); # OK
            self.send_header('Content-type', 'image/svg+xml');
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers();
            self.wfile.write(svgContent.encode())
            # self.wfile.write(bytes(svgContent, "utf-8"))

            # self.sendMessage(message)

        elif(self.path == '/rotateMoleculeForm'):
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);
            # content = body.decode( 'utf-8' )
            # print(body)
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );            
            # print("POSTVARS", postvars)
            # print("LEN", len(postvars))
            correctFlag = 0
            
            # print(postvars['fData[ROTATION_ANGLE]'])
            # print(postvars['dropdownV'])
            
            if(len(postvars) != 2):
                correctFlag = 1
                message = "Please pick an rotation type and angle."
            else:
                angle = postvars['fData[ROTATION_ANGLE]'][0]

                try:
                    angle = int(angle)
                except Exception as e:
                    message = "Incorrect Angle"
                axis = postvars['dropdownV'][0]
                # print("angle: ", angle, "axis: ", axis)
                message = "Rotate angle"
                
                try:
                    sentMolName
                    # print("Molecule name: ", sentMolName)
                except Exception as e:
                    correctFlag = 1
                    message = "Please pick a molecule first."                

                if(correctFlag == 0):
                    svgLines = self.rotateMolecule(sentMolName, angle, axis)
                    # print(svgLines)
                
            # sentMolName = None

            if(correctFlag == 0):
                self.send_response( 200 ); # OK
                self.send_header('Content-type', 'image/svg+xml');
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers();
                self.wfile.write(svgLines.encode())
            
        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );
    
    # Send message back to JQuery
    def sendMessage(self, message):
        self.send_response( 200 );
        self.send_header( "Content-type", "text/plain" );
        self.send_header( "Content-length", len(message) );
        self.end_headers();
        self.wfile.write( bytes( message, "utf-8" ) );

    # chcecks if file ends with .sdf
    def correctFilename(self, content):
        findfile = 'filename="(.+)"'
        flag = re.search(findfile, content.decode('utf-8'))
        
        if flag:
            fileName = flag.group(1)
            if fileName.endswith('.sdf'):
                return 0
            else: 
                return 1
        else:
            return 1

    # Create the element page html
    def createElementPage(self):
        
        self.send_response(200)
        message = htmlHeader 
        
        # Get list of elements in database
        eleList = sq.listOfElements();  
        elements = []
        for i in range(len(eleList)):
            eleList[i] = str(eleList[i])
            cur = re.findall(r"'([^']*)'", eleList[i])
            elements.append(cur)

        message += """
        <div class="elementClass">
        <h1>Update Elements</h1>
        <h2>Delete Element</h2>
        <div class="delFormClass>
        <form name="elementDelForm">
            <select id="elementDropdown" name="elementDropdown">
        """
        # Create a dropdown of all the elements
        message += "<option value="">Select an element</option>"
        for i in elements:
            if(i[0] != 'Default1'):
                message += f'<option value = "{i}">{i[0]}</option>'
        message += """
            </select><br><br>
            
            <button type="button" id="elementDelFormSubmit">Delete Element</button>
        </form></div> <br>
        """
        message += htmlElementForm + "</div>" + htmlFooter
        return message

    # Creates a list of molecules that can be displayed
    def createListPage(self):
        # self.send_response(200)
        message = htmlHeader;
        message+="""<div class = "uploadClass"> <h1>Molecule List</h1> <h2>Select a molecule to view.</h2>"""
        message += """
        <form name="moleculeForm" id="moleculeForm">
        """
        # List of molecules
        moleculeList = sq.listOfMolecules()
        atomCount = sq.moleculeAtomsCount()
        bondCount = sq.moleculeBondsCount()

        moleculeNames = []
        # Get list of molecules
        for i in range(len(moleculeList)):
            moleculeList[i] = str(moleculeList[i])
            cur = re.findall(r"'([^']*)'", moleculeList[i])
            moleculeNames.append(cur)
        # Update for buttons to show atom and bond count
        for i in range(len(moleculeNames)):
            message += f'<button type="submit" title="Atoms: {atomCount[i]} Bonds: {bondCount[i]}" name="mol" value="{moleculeNames[i][0]}" data-path="/moleculeForm">{moleculeNames[i][0]}</button>'
        message += htmlRotateMolecule;
        message += """
        </form> <br>
        <h3>Molecule (No rotations)</h3>
        <div id="molSVGImg"></div>
        <h3>Molecule (Rotated)</h3>
        <div id="rotateSVGImg"></div>
        </div>
        """ + htmlFooter
        return message

    # Function to get molecule SVG 
    def displayMolecule(self, molName):
        MolDisplay.radius = sq.radius();
        MolDisplay.element_name = sq.element_name();
        MolDisplay.header += sq.radial_gradients();
        mol = sq.load_mol(molName)
        mol.sort()
        return mol.svg()

    def rotateMolecule(self, molName, angle, axis):
        MolDisplay.radius = sq.radius();
        MolDisplay.element_name = sq.element_name();
        MolDisplay.header += sq.radial_gradients();
        mol = sq.load_mol(molName)
        mol.sort()
        if(axis == 'X'):
            mx = molecule.mx_wrapper(angle,0,0);
        elif(axis == 'Y'):
            mx = molecule.mx_wrapper(0,angle,0);
        elif(axis == 'Z'):
            mx = molecule.mx_wrapper(0,0,angle);
        mol.xform( mx.xform_matrix );
        return mol.svg()



# httpd = HTTPServer( ( 'localhost', int(sys.argv[1] ), MyHandler );
httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler );

sq = Database(reset=True);
sq.create_tables();
sq['Elements'] = (120,'D1', 'Default1', '008000', '800080', 'FF0000', 25 );
htmlHeader = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset='utf-8'>
        <meta http-equiv='X-UA-Compatible' content='IE=edge'>
        <title>Molecule Viewer</title>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    
        <script src='script.js'></script>
        <link href="style.css" rel="stylesheet">
    </head>
    <body>
    

    <div class="navbar">
        <a class="active" href="index.html">Home</a>
        <a href="update.html">Update Elements</a>
        <a href="upload.html">Upload File</a>
        <a href="list.html">Molecule Display</a>
    </div>
    """

htmlFooter = """
</body>
</html>
"""

htmlElementForm = """
    <h2>Add Element</h2>
    <form name="elementForm">
        <label for="ELEMENT_NO">Element Number:</label>
        <input type="number" id="ELEMENT_NO" name="ELEMENT_NO"><br><br>
        <label for="ELEMENT_CODE">Element Code:</label>
        <input type="text" id="ELEMENT_CODE" name="ELEMENT_CODE"><br><br>

        <label for="ELEMENT_NAME">Element Name:</label>
        <input type="text" id="ELEMENT_NAME" name="ELEMENT_NAME"><br><br>

        <label for="COLOUR1">Element Colour 1:</label>
        <input type="color" id="COLOUR1" name="COLOUR1" value="#FFA500"><br><br>

        <label for="COLOUR2">Element Colour 2:</label>
        <input type="color" id="COLOUR2" name="COLOUR2" value="#FFFF00"><br><br>

        <label for="COLOUR3">Element Colour 3:</label>
        <input type="color" id="COLOUR3" name="COLOUR3" value="#A020F0"><br><br>

        <label for="RADIUS">Radius:</label>
        <input type="number" id="RADIUS" name="RADIUS"><br><br>

        <button type="button" id="elementFormSubmit">Upload Element</button>
    </form>

"""

htmlRotateMolecule =  """
<h2>Rotate Molecule</h2>
<br><form name="rotateMoleculeForm">
<select id="rotateDropdown" name="rotateDropdown">
    <option value="">Select rotation type</option>
    <option value="X">X Rotation</option>
    <option value="Y">Y Rotation</option>
    <option value="Z">Z Rotation</option>
</select>    
    <p>
        <label for="ROTATION_ANGLE">Angle:</label>
        <input type="number" id="ROTATION_ANGLE" name="ROTATION_ANGLE value="0"><br>
    </p>
    
    <p>
        <button type="button" id="moleculeRotationFormSubmit">Rotate</button>
    </p>
</form>
"""



httpd.serve_forever();

