import os;
import sqlite3;
from MolDisplay import Atom;
from MolDisplay import Bond;
from MolDisplay import Molecule
import molecule;
import MolDisplay;

class Database:
    
    def __init__(self, reset=False): #can i leave it as reset
        #if reset is true, remove the current data base
        if(reset):
            if os.path.exists( 'molecules.db' ):
                os.remove('molecules.db')
       
        # connect to sqlite
        self.conn = sqlite3.connect('molecules.db')
        # create cursor used for sql
        self.c = self.conn.cursor()

    # Create tables for database
    def create_tables(self):
        # Elements
        self.conn.execute( """CREATE TABLE Elements ( 
             		ELEMENT_NO    INTEGER      NOT NULL,
             		ELEMENT_CODE  VARCHAR(3)  NOT NULL,
             		ELEMENT_NAME  VARCHAR(32) NOT NULL,
             		COLOUR1       CHAR(6)     NOT NULL,
                    COLOUR2       CHAR(6)     NOT NULL,
                    COLOUR3       CHAR(6)     NOT NULL,
                    RADIUS        DECIMAL(3)  NOT NULL,
             		PRIMARY KEY (ELEMENT_CODE) );""" );
                

        # Atoms
        self.conn.execute( """CREATE TABLE Atoms ( 
             		ATOM_ID       INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
             		ELEMENT_CODE  VARCHAR(3)            NOT NULL,
             		X             DECIMAL(7,4)          NOT NULL,
                    Y             DECIMAL(7,4)          NOT NULL,
                    Z             DECIMAL(7,4)          NOT NULL,
                    FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements(ELEMENT_CODE) );""" );

        # Bonds
        self.conn.execute( """CREATE TABLE Bonds ( 
             		BOND_ID    INTEGER PRIMARY KEY  AUTOINCREMENT   NOT NULL,
             		A1         INTEGER      NOT NULL,
             		A2         INTEGER      NOT NULL,
                    EPAIRS     INTEGER      NOT NULL );""" );

        # Molecules 
        self.conn.execute( """CREATE TABLE Molecules ( 
             		MOLECULE_ID    INTEGER PRIMARY KEY AUTOINCREMENT  NOT NULL,
             		NAME           TEXT  UNIQUE NOT NULL );""" );

        # MoleculeAtom
        self.conn.execute( """CREATE TABLE MoleculeAtom ( 
             		MOLECULE_ID    INTEGER      NOT NULL,
             		ATOM_ID        INTEGER      NOT NULL,
             		PRIMARY KEY (MOLECULE_ID,ATOM_ID), 
                    FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                    FOREIGN KEY (ATOM_ID) REFERENCES Atoms(ATOM_ID) );""" );

        # MoleculeBond
        self.conn.execute( """CREATE TABLE MoleculeBond ( 
             		MOLECULE_ID    INTEGER      NOT NULL,
             		BOND_ID        INTEGER      NOT NULL,
             		PRIMARY KEY (MOLECULE_ID,BOND_ID), 
                    FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
                    FOREIGN KEY (BOND_ID) REFERENCES Bonds(BOND_ID)  );""" );

        # default elements
        self.conn.execute( """CREATE TABLE defElements ( 
             		ELEMENT_CODE  VARCHAR(3)  NOT NULL,
             		ELEMENT_NAME  VARCHAR(32) NOT NULL,
             		COLOUR1       CHAR(6)     NOT NULL,
                    COLOUR2       CHAR(6)     NOT NULL,
                    COLOUR3       CHAR(6)     NOT NULL,
                    RADIUS        DECIMAL(3)  NOT NULL,
             		PRIMARY KEY (ELEMENT_CODE) );""" );

        self.conn.commit()

    
    # set table
    def __setitem__( self, table, values ):
        if(table == "Elements"):
            self.conn.execute("INSERT INTO {} VALUES (?,?,?,?,?,?,?)".format(table), (values[0], values[1], values[2],values[3],values[4], values[5],  values[6]))
            self.conn.commit()
        if(table == "Atoms"):
            self.cursorUsed = self.conn.execute("INSERT INTO Atoms(ELEMENT_CODE, X, Y, Z) VALUES (?, ?, ?, ?)", (values[0], values[1], values[2],values[3]))
            self.conn.commit()
        
        if(table == "Bonds"):
            self.cursorUsed = self.conn.execute("INSERT INTO Bonds(A1,A2,EPAIRS) VALUES (?,?,?)", (values[0], values[1], values[2]))
            self.conn.commit()
        
        if(table == "Molecules"):
            self.conn.execute("INSERT INTO Molecules(NAME) VALUES (?)", (values[0],))
            self.conn.commit()

        if(table == "MoleculeAtom"):
            self.conn.execute("INSERT INTO MoleculeAtom(MOLECULE_ID,ATOM_ID) VALUES (?,?)", (values[0], values[1]))
            self.conn.commit()

        if(table == "MoleculeBond"):
            self.conn.execute("INSERT INTO MoleculeBond(MOLECULE_ID, BOND_ID) VALUES (?,?)", (values[0], values[1]))
            self.conn.commit()
        
        if(table == "defElements"):
            self.conn.execute("INSERT INTO {} VALUES (?,?,?,?,?,?)".format(table), (values[0], values[1], values[2],values[3],values[4], values[5]))
            self.conn.commit()
    
    def add_atom( self, molname, atom ):

        # Insert atom into Atoms table
        v = [atom.element, atom.x, atom.y, atom.z]
        self.__setitem__('Atoms', v)  

        
        # Get the id for the last insertion in Atoms table
        aId = self.cursorUsed.lastrowid

        # SQL statement that gets the molecule_id given the name
        self.c.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?", (molname,))
        
        # stored, note its a tuple has [0]
        mId = self.c.fetchone()[0]
        # insert into MoleculeAtom
        v = [mId, aId]
        self.__setitem__('MoleculeAtom', v)  

        

    def add_bond( self, molname, bond ):
        # SQL statement to insert bond into Bonds table
        v = [bond.a1, bond.a2,bond.epairs]
        self.__setitem__('Bonds', v)  

        # get bond id
        bId = self.cursorUsed.lastrowid

        # are bonds supposed to be 0?

        # SQL statement that gets the molecule_id given the name
        self.c.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?", (molname,))
        # get molecule id
        mId = self.c.fetchone()[0]
        # insert into MoleculeBond table using the ids
        v = [mId, bId]
        self.__setitem__('MoleculeBond', v)  
        

    def add_molecule( self, name, fp ):
        # make object of Molecule and parse file
        mol = Molecule()
        mol.parse(fp)
        # SVG = mol.svg()
        # insert into Molecule table
        v = [name]
        self.__setitem__('Molecules', v)  

        
        # iterate and add all the atoms and bonds of molecule into the respective tables
        for i in range(mol.atom_no):
            atom = mol.get_atom(i)
            self.add_atom(name, atom)

        for i in range(mol.bond_no):
            bond = mol.get_bond(i)
            self.add_bond(name, bond)
        

    def load_mol( self, name ):
        # SQL statement gets all the atoms given the molecule name, in increasing ATOM_ID order
        self.c.execute("""
            SELECT Atoms.* 
            FROM Molecules 
            JOIN MoleculeAtom ON Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID 
            JOIN Atoms ON MoleculeAtom.ATOM_ID = Atoms.ATOM_ID 
            WHERE Molecules.NAME = ? 
            ORDER BY Atoms.ATOM_ID ASC;
            """, (name,))

        atomList = self.c.fetchall()
        mol = Molecule()

        # iterate through atomList and append each atom
        for i in atomList:
            
            iD, element, x, y, z = i
            mol.append_atom(element, x, y, z)
        
        # SQL statement gets all the bonds given the molecule name, in increasing BOND_ID order

        self.c.execute("""
            SELECT Bonds.* 
            FROM Molecules 
            JOIN MoleculeBond ON Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID 
            JOIN Bonds ON MoleculeBond.BOND_ID = Bonds.BOND_ID 
            WHERE Molecules.NAME = ? 
            ORDER BY Bonds.BOND_ID ASC;
            """, (name,))

        bondList = self.c.fetchall()

        # iterate through bondList and append each atom
        for i in bondList:
            iD, a1, a2, e = i
            mol.append_bond(a1, a2, e)
        
        return mol

    def radius( self ):

        # SQL statement get the radius from element code for everything in the Elements table
        self.c.execute("SELECT ELEMENT_CODE, RADIUS FROM Elements")
        rad = self.c.fetchall()
        # return dictionary with all the radii
        return {ele[0]: ele[1] for ele in rad}

        
    def element_name( self ):
        # SQL statement get the element name and element from all the Elements table
        self.c.execute("SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements")
        name = self.c.fetchall()
        # return dictionary with element code and name
        return {i[0]: i[1] for i in name}

    
    def radial_gradients( self ):
        svg = ""
        self.c.execute("SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements")
        elementList = self.c.fetchall()
        # iterate through every element
        for i in elementList:
            elementName, c1, c2, c3 = i
            # create svg for element
            radialGradientSVG = """
                <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
                <stop offset="0%%" stop-color="#%s"/>
                <stop offset="50%%" stop-color="#%s"/>
                <stop offset="100%%" stop-color="#%s"/>
                </radialGradient>""" %(elementName, c1, c2, c3)
            # append it to svg string
            svg = svg + radialGradientSVG

        return svg

    # Checks if a molecule name is unique
    def uniqueMolecule(self, molName):
        self.c.execute("SELECT EXISTS(SELECT 1 FROM Molecules WHERE NAME='{}')".format(molName))
        val  = self.c.fetchall()
        return val[0][0]

    # Returns a list of elements
    def listOfElements(self):
        self.c.execute("SELECT ELEMENT_NAME from Elements")
        elementList = self.c.fetchall()
        return elementList

    # Delete element 
    def deleteElement(self, elementName):
        self.c.execute("DELETE FROM Elements WHERE ELEMENT_NAME = ?", (elementName,))
        self.conn.commit()

    # Check if the element name and element code are unique before inserting
    def uniqueElement(self, elementName, elementCode):
        self.c.execute("SELECT EXISTS(SELECT 1 FROM Elements WHERE ELEMENT_NAME='{}')".format(elementName))
        val  = self.c.fetchall()
        self.c.execute("SELECT EXISTS(SELECT 1 FROM Elements WHERE ELEMENT_CODE='{}')".format(elementCode))
        val1  = self.c.fetchall()
        print("val0: ", val[0][0], "val1: ", val1[0][0])
        return val[0][0] + val1[0][0]

    # Returns list of all molecules

    def listOfMolecules(self):
        self.c.execute("SELECT NAME from Molecules")
        moleculeList = self.c.fetchall()
        return moleculeList

    # Returns atom count of all molecules

    def moleculeAtomsCount(self):
        self.c.execute("SELECT COUNT(*) FROM Molecules")
        molCount = self.c.fetchone()[0]
        
        atomCount = []
        for i in range (molCount):
            self.c.execute("SELECT COUNT(*) FROM MoleculeAtom WHERE MOLECULE_ID = ?", (i+1,))
            count = self.c.fetchone()[0]
            atomCount.append(count)
        
        return atomCount

    # Returns bond count of all molecules
    def moleculeBondsCount(self):
        self.c.execute("SELECT COUNT(*) FROM Molecules")
        molCount = self.c.fetchone()[0]
        
        bondCount = []
        for i in range (molCount):
            self.c.execute("SELECT COUNT(*) FROM MoleculeBond WHERE MOLECULE_ID = ?", (i+1,))
            count = self.c.fetchone()[0]
            bondCount.append(count)
        
        return bondCount
