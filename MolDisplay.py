import molecule;
import re;
import math;

'''
radius = { 'H': 25,
            'C': 40,
            'O': 40,
            'N': 40,
};

element_name = { 'H': 'grey',
                'C': 'black',
                'O': 'red',
                'N': 'blue',
};
'''

header = """<svg version="1.1" width="1000" height="1000"
xmlns="http://www.w3.org/2000/svg">""";
footer = """</svg>""";
offsetx = 500;
offsety = 500;


class Atom:

    # Constructor, stores atom and atom's z value
    def __init__(self, c_atom):
        self.c_atom = c_atom;
        self.z = c_atom.z;

    # Do i need get and set methods?
    def get_c_atom(self):
        return self.c_atom;

    # to string method display atom's x,y,z,element
    def __str__(self):
        return '%s %f %f %f' % (self.c_atom.element, self.c_atom.x, self.c_atom.y, self.c_atom.z);

    # Calculate x,y coordinate of the centre of the circle representing the atom, radius and colour of atom
    def svg(self):

        centreX = (self.c_atom.x * 100.0) + offsetx;
        centreY = (self.c_atom.y * 100.0) + offsety;
        try:
            radAtom = radius[self.c_atom.element];
        except Exception as e:
            radAtom =  radius['D1'];
        try:
            colAtom = element_name[self.c_atom.element];
        except Exception as e:
            colAtom = element_name['D1']
        return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' %(centreX, centreY, radAtom, colAtom);

class Bond:

    # Constructor, stores bond and bond's z value
    def __init__(self,c_bond):
        self.c_bond = c_bond;
        self.z = c_bond.z;

    # to stirng that returns x values, y values, z, len, dx and dy
    def __str__(self):
        return 'x1:%f x2:%f y1:%f y2:%f z:%f len:%f dx:%f dy:%f' %(self.c_bond.x1, self.c_bond.x2, self.c_bond.y1, self.c_bond.y2, self.z, self.c_bond.len, self.c_bond.dx, self.c_bond.dy);

    # determines the corners of the rectangle representing the bonds of an atom
    def svg(self):
        # calculate the centres of a1 and a2 of bond
        cX1 = (self.c_bond.x1 * 100) + offsetx;
        cY1 = (self.c_bond.y1 * 100) + offsety;

        cX2 = (self.c_bond.x2 * 100) + offsetx;
        cY2 = (self.c_bond.y2 * 100) + offsety;

        ax = cX1 - self.c_bond.dy * 10.0;
        ay = cY1 - self.c_bond.dx * 10.0;

        bx = cX1 + self.c_bond.dy * 10.0;
        by = cY1 + self.c_bond.dx * 10.0;

        cx = cX2 + self.c_bond.dy * 10.0;
        cy = cY2 + self.c_bond.dx * 10.0;

        dx = cX2 - self.c_bond.dy * 10.0;
        dy = cY2 - self.c_bond.dx * 10.0;

        p1 = (ax, ay);
        p2 = (bx, by);
        p3 = (cx, cy);
        p4 = (dx, dy);

        # vector calculation between the first triangle points
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])

        #Calculate dot product
        dotProduct = v1[0] * v2[0] + v1[1] * v2[1];

        # Calculate magnitude of vectors
        magV1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2);
        magV2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2);

        # Calculate the angle between the vectors in degrees
        angle = math.degrees(math.acos(dotProduct / (magV1* magV2)))

        # The angle should approximately be close to 90deg, if its not swap the y coordinate between the 2 points
        if(angle < 85 or angle > 95):
            temp = ay;
            ay = by;
            by = temp;

        # Repeat the process for the second triangle in the rectangle

        v1 = (p2[0] - p1[0], p2[1] - p1[1])
        v2 = (p4[0] - p1[0], p4[1] - p1[1])

        dotProduct = v1[0] * v2[0] + v1[1] * v2[1];

        magV1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2);
        magV2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2);
        angle = math.degrees(math.acos(dotProduct / (magV1 * magV2)))

        if(angle < 85 or angle > 95):
            temp = cy;
            cy = dy;
            dy = temp;

        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' %(ax, ay, bx, by, cx, cy, dx, dy);


class Molecule(molecule.molecule):

    # prints all the atoms and bonds
    def __str__(self):
        s = "Atom Max: %d Atom No: %d\n" %(self.atom_max, self.atom_no);
        for i in range(self.atom_no):
            s = s + str(Atom(mol.get_atom(i))) +"\n";
        s = s + "Bond Max: %d Bond No: %d\n" %(self.bond_max, self.bond_no);
        for i in range(self.atom_no):
            s = s + str(Bond(mol.get_bond(i))) +"\n";
        return s;

    # creates an svg string of the molecule, that is ordered in the correct bond and atom order
    def svg(self):

        a = [];
        b = [];
        # Sort bonds and atoms in ascending order by Z value
        molecule.molsort(self);

        # atoms are stored in a
        for i in range(self.atom_no):
            a.append(Atom(self.get_atom(i)));

        # bonds stored in b
        for i in range(self.bond_no):
            b.append(Bond(self.get_bond(i)));

        svgOrder = [];

        aIndex = 0;
        bIndex = 0;
        s=""

        # add bonds and atoms, depending on whose z value is lower, all bonds and atoms are eventually added
        while((aIndex < self.atom_no) and (bIndex < self.bond_no)):
            if (a[aIndex].z < b[bIndex].z):
                svgOrder.append(a[aIndex]);

                s = s + a[aIndex].svg();
                aIndex+=1;
            elif (b[bIndex].z < a[aIndex].z):
                svgOrder.append(b[bIndex]);
                s = s + b[bIndex].svg();
                bIndex+=1;


        while(aIndex < self.atom_no):
            svgOrder.append(a[aIndex]);
            s = s + a[aIndex].svg();
            aIndex+=1;

        while(bIndex < self.bond_no):
            svgOrder.append(b[bIndex]);
            s = s + b[bIndex].svg();
            bIndex+=1;

        return f'{header}{s}{footer}';

    # parse the file and append the molecule's bonds and atoms into the structure
    # the parsing is done using regex
    def parse(self, file):

        l = [];
        content = [line.strip() for line in file.readlines()]


        molInfo = content[3];
        content = content[4:]

        # First line has the number of bonds and atoms
        for i in re.findall(r'\d+', molInfo):
            l.append(i)

        self.atom_max = 0;
        self.bond_max = 0;

        atomMax = int(l[0]);
        bondMax = int(l[1]);
        self.atom_no = 0;
        self.bond_no = 0;

        lineCount = 0;
        # collect the x,y,z and element of an atom, and append it to atom
        for j in range(atomMax):
            g = [];
            for i in re.findall(r'-?\d+(?:\.\d+)?',content[lineCount]):
                g.append(i);
            x = float(g[0]);
            y = float(g[1]);
            z = float(g[2]);
            k = [];

            for i in re.findall(r'[a-zA-Z]+', content[lineCount]):
                k.append(i);

            element = k[0];
            self.append_atom(element, x, y, z);
            lineCount+=1;

        # collect the data for each bond and append
        for i in range(bondMax):
            g = [];
            for i in re.findall(r'\d+(?:\.\d+)?',content[lineCount]):
                g.append(i);


            a1 = int(g[0]);
            a1 = a1 - 1; #could be wrong
            a2 = int(g[1]);
            a2 = a2 -1; #could be wrong
            e = int(g[2]);
            self.append_bond(a1, a2, e);
            lineCount+=1;

# where do i put the -1 
