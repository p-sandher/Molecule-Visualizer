#include "mol.h"

/*
   atomset: populates an atom
*/
void atomset( atom *atom, char element[3], double *x, double *y, double *z ){
   if (atom != NULL){
      atom->x = *x;
      atom->y = *y;
      atom->z = *z;
      strcpy(atom->element, element);
   }
}

/*
   atomget: get the contents of an atom
*/
void atomget( atom *atom, char element[3], double *x, double *y, double *z ){
   *x = atom->x;
   *y = atom->y;
   *z = atom->z;

   strcpy(element, atom->element);
}

/*
   bondset: populates a bond
*/
void bondset(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
   bond->a1 = *a1;
   bond->a2 = *a2;
   bond->atoms = *atoms;
   bond->epairs = *epairs;
   compute_coords(bond);
}


/*
   compute_coords: finds bonds' x,y,z for both atoms. Calculates the z,len,dx and dy
*/
void compute_coords(bond *bond) {
   bond->x1 = bond->atoms[bond->a1].x;
   bond->y1 = bond->atoms[bond->a1].y;
   bond->x2 = bond->atoms[bond->a2].x;
   bond->y2 = bond->atoms[bond->a2].y;
   bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2.0;

   // bond->len = pow(pow((bond->x2 - bond->x1),2) + pow((bond->y2 - bond->y1),2) + pow((bond->atoms[bond->a1].z - bond->atoms[bond->a2].z),2), 0.5);
   bond->len = sqrt(pow((bond->x2 - bond->x1),2) + pow((bond->y2 - bond->y1),2));
   bond->dx = fabs((bond->x2 - bond->x1)) / bond->len;
   bond->dy = fabs((bond->y2 - bond->y1)) / bond->len;
}


/*
   bond_comp: compares Z values of 2 atoms by calculating the average. Returns -1,0 or 1 depending on the comparison.
   This function is called with qsort
*/
int bond_comp(const void *a, const void *b) {
   struct bond *b1Ptr, *b2Ptr;
   int res = 0;
   b1Ptr = *(struct bond **) a;
   b2Ptr = *(struct bond **) b;

   float b1AtomAvg = ((b1Ptr->atoms[b1Ptr->a1].z) + (b1Ptr->atoms[b1Ptr->a2].z)) / 2.0;
   float b2AtomAvg = ((b2Ptr->atoms[b2Ptr->a1].z) + (b2Ptr->atoms[b2Ptr->a2].z)) / 2.0;

   if(b1AtomAvg > b2AtomAvg){
      res = 1;
   } else if (b1AtomAvg < b2AtomAvg) {
      res = -1;
   } else {
      res = 0;
   }
   return res;
}


/*
   bondget: get the contents of a bond
*/

void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ) {
   *a1 = bond->a1;
   *a2 = bond->a2;
   *epairs = bond->epairs;
   *atoms = bond->atoms;
}


/*
   molmalloc: allocates memory for a new molecule, returning the address of the molecule
*/
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ){
   molecule *newMolecule = malloc(sizeof(molecule));
   newMolecule->atom_max = atom_max;
   newMolecule->atom_no = 0;

   newMolecule->atoms = (atom*)malloc(sizeof(atom)*atom_max);
   if(newMolecule->atoms == NULL){
      fprintf(stderr,"malloc failed\n");
      molfree(newMolecule);
      return NULL;
   }

   newMolecule->atom_ptrs = (atom**)malloc(sizeof(atom *)*atom_max);
   if(newMolecule->atom_ptrs == NULL){
      fprintf(stderr,"malloc failed\n");
      molfree(newMolecule);
      return NULL;
   }

   newMolecule->bond_max = bond_max;
   newMolecule->bond_no = 0;

   newMolecule->bonds = (bond*)malloc(sizeof(bond)*bond_max);
   if(newMolecule->bonds == NULL){
      fprintf(stderr,"malloc failed\n");
      molfree(newMolecule);
      return NULL;
   }
   newMolecule->bond_ptrs = (bond**)malloc(sizeof(bond *)*bond_max);
   if(newMolecule->bond_ptrs == NULL){
      fprintf(stderr,"malloc failed\n");
      molfree(newMolecule);
      return NULL;
   }
   return newMolecule;
}

/*
   molcopy: makes a copy of a molecule by allocating memory, and appending all atoms and bonds
   returns its address
*/
molecule *molcopy( molecule *src ){

   molecule *moleculeCopy =  molmalloc(src->atom_max,src->bond_max);
   // check null

   if( moleculeCopy == NULL ){
      molfree(src);
      return NULL;
   }

   moleculeCopy->bond_max = src->bond_max;
   moleculeCopy->atom_max = src->atom_max;

   for(int i = 0; i < src->atom_no; i++){
      molappend_atom(moleculeCopy, &(src->atoms[i]));
   }
   for(int i = 0; i < src->bond_no; i++){
      molappend_bond(moleculeCopy, &(src->bonds[i]));
   }
   return moleculeCopy;
}

/*
   molfree: frees a molecule
*/
void molfree( molecule *ptr ){

   free(ptr->atoms);
   free(ptr->atom_ptrs);

   free(ptr->bonds);

   free(ptr->bond_ptrs);
   free(ptr);
}

/*
   molappend_atom: appends an atom to the next availble spot in the atoms array of a molecule
*/
void molappend_atom( molecule *molecule, atom *atom ) {

   if(molecule->atom_max == 0){
      molecule->atom_max = 1;
      molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * (molecule->atom_max));
      if(molecule->atoms == NULL){
         fprintf(stderr,"Realloc failed\n");
         molfree(molecule);
         exit(1);
      }
      molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * (molecule->atom_max));
      if(molecule->atom_ptrs == NULL){
         fprintf(stderr,"Realloc failed\n");
         molfree(molecule);
         exit(1);
      }
   }

   if( molecule->atom_no >= molecule->atom_max ) {
      (molecule->atom_max) *= 2;
      molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * (molecule->atom_max));
      if(molecule->atoms == NULL){
         fprintf(stderr,"Realloc failed\n");
         molfree(molecule);
         exit(1);
      }

      molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * (molecule->atom_max));
      if(molecule->atom_ptrs == NULL){
         fprintf(stderr,"Realloc failed\n");
         molfree(molecule);
         exit(1);
      }
   }

   memcpy(&(molecule->atoms[molecule->atom_no]), atom, sizeof(struct atom));

   (molecule->atom_no)++;

   for(int i =  0; i < molecule->atom_no; i++){
      (molecule->atom_ptrs)[i] = &((molecule->atoms)[i]);
   }
}

/*
   moleappend_bond: appends a bond to the next availble spot in the bonds array of a molecule
*/
void molappend_bond(molecule *molecule,bond *bond ){

   if(molecule->bond_max == 0){
      molecule->bond_max = 1;
      molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * (molecule->bond_max));
      if(molecule->bonds == NULL){
         fprintf(stderr,"Realloc failed\n");
         molfree(molecule);
         exit(1);
      }
      molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * (molecule->bond_max));
      if(molecule->bond_ptrs == NULL){
         fprintf(stderr,"Realloc failed\n");
         molfree(molecule);
         exit(1);
      }
   }

   if( molecule->bond_no >= molecule->bond_max ) {
      (molecule->bond_max) *= 2;
      molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * (molecule->bond_max));
      if(molecule->bonds == NULL){
         fprintf(stderr,"Realloc failed\n");
         molfree(molecule);
         exit(1);
      }
      molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * (molecule->bond_max));
      if(molecule->bond_ptrs == NULL){
         fprintf(stderr,"Realloc failed\n");
         molfree(molecule);
         exit(1);
      }
   }

   memcpy(&(molecule->bonds[molecule->bond_no]), bond, sizeof(struct bond));

   (molecule->bond_no)++;

   for(int i =  0; i < molecule->bond_no; i++){
      (molecule->bond_ptrs)[i] = &((molecule->bonds)[i]);
   }
}

/*
   sortAtoms: compares Z values of 2 atoms. Returns -1,0 or 1 depending on the compariosn.
   This function is called with qsort
*/
int sortAtoms(const void *a1, const void *a2){
   struct atom *a1Ptr, *a2Ptr;
   int res = 0;
   a1Ptr = *(struct atom **) a1;
   a2Ptr = *(struct atom **) a2;

   if((a1Ptr->z) > (a2Ptr->z)){
      res = 1;
   } else if ((a1Ptr->z) < (a2Ptr->z)) {
      res = -1;
   } else {
      res = 0;
   }
   return res;
}



/*
   molsort: sorts atoms and bonds by Z values using qsort.
   This manipulates atom_ptrs and bond_ptrs
*/
void molsort( molecule *molecule ){
   qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(struct atom*), sortAtoms);
   qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(struct bond*), bond_comp);

}

/*
   xrotation: populates the xform_matrix of 3D X-rotation given a specified degree
*/
void xrotation( xform_matrix xform_matrix, unsigned short deg ){
   double degInRad = deg * PI / 180.0;
   xform_matrix[0][0] = 1;
   xform_matrix[0][1] = 0;
   xform_matrix[0][2] = 0;
   xform_matrix[1][0] = 0;
   xform_matrix[1][1] = cos(degInRad);
   xform_matrix[1][2] = -sin(degInRad);
   xform_matrix[2][0] = 0;
   xform_matrix[2][1] = sin(degInRad);
   xform_matrix[2][2] = cos(degInRad);

}

/*
   yrotation: populates the xform_matrix of 3D Y-rotation given a specified degree
*/
void yrotation( xform_matrix xform_matrix, unsigned short deg ){
   double degInRad = deg * PI / 180.0;
   xform_matrix[0][0] = cos(degInRad);
   xform_matrix[0][1] = 0;
   xform_matrix[0][2] = sin(degInRad);
   xform_matrix[1][0] = 0;
   xform_matrix[1][1] = 1;
   xform_matrix[1][2] = 0;
   xform_matrix[2][0] = -sin(degInRad);
   xform_matrix[2][1] = 0;
   xform_matrix[2][2] = cos(degInRad);

}


/*
   zrotation: populates the xform_matrix of 3D Z-rotation given a specified degree
*/
void zrotation( xform_matrix xform_matrix, unsigned short deg ){
   double degInRad = deg * PI / 180.0;
   xform_matrix[0][0] = cos(degInRad);
   xform_matrix[0][1] = -sin(degInRad);
   xform_matrix[0][2] = 0;
   xform_matrix[1][0] = sin(degInRad);
   xform_matrix[1][1] = cos(degInRad);
   xform_matrix[1][2] = 0;
   xform_matrix[2][0] = 0;
   xform_matrix[2][1] = 0;
   xform_matrix[2][2] = 1;

}


/*
   mol_xform: Applies the transformation of the given matrix to the x,y,z
   coordinates of all the atoms in the molecule
*/
void mol_xform(molecule *molecule, xform_matrix matrix){
   double currentX = 0;
   double currentY = 0;
   double currentZ = 0;

   for(int i = 0; i < molecule->bond_no; i++) {
      compute_coords(&((molecule->bonds)[i]));
   }


   for(int i = 0;  i < molecule->atom_no; i++){
      currentX = molecule->atoms[i].x;
      currentY = molecule->atoms[i].y;
      currentZ = molecule->atoms[i].z;

      molecule->atoms[i].x = (matrix[0][0] * currentX) + (matrix[0][1] * currentY) + (matrix[0][2] * currentZ);
      molecule->atoms[i].y = (matrix[1][0] * currentX) + (matrix[1][1] * currentY) + (matrix[1][2] * currentZ);
      molecule->atoms[i].z = (matrix[2][0] * currentX) + (matrix[2][1] * currentY) + (matrix[2][2] * currentZ);
   }

   for(int i = 0; i < molecule->bond_no; i++) {
      // compute_coords(&molecule->bonds[i]);
      compute_coords(&((molecule->bonds)[i]));
   }
}
