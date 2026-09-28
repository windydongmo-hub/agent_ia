import psycopg 

class Memoire:
    def __init__(self):
        #self.nom = nom
        self.connexion = psycopg.connect( 
            host = "localhost",
            dbname = "postgres",
            user  = "postgres",
            password = "675753411",
            port = 5432 )
        self.curseur = self.connexion.cursor()

    def rechercher (self , nom, mot):
       requete = """ select m.contenu from agents as a join memoires as m on a.id = m.agent_id  where a.nom = %s and m.contenu ilike %s; """
       
       self.curseur.execute(requete , (nom , "%" + mot +"%")) 
        
       resultat = self.curseur.fetchall()
       return resultat
    def fermer(self):
       self.curseur.close()
       self.connexion.close()
       return "La connexion est bien fermer" 
    def recherche_id(self , nom):
       requete = """ select a.id from agents as a where a.nom  ilike %s;  """ 
       self.curseur.execute(requete , (nom,) )
       resultat = self.curseur.fetchone()
       if resultat is None:
           return None
       return resultat[0]
    def ajouter(self , contenu ,nom):
        identifiant = self.recherche_id(nom)
        if identifiant is None: 
           return False
        agent_id = identifiant
        requete =  """ insert into memoires (agent_id , contenu ) values ( %s,  %s) returning id , agent_id , contenu;  """
        
        self.curseur.execute( requete , (agent_id , contenu))
        memoire_id = self.curseur.fetchone()
        self.connexion.commit()
        return memoire_id
    def afficher(self , nom ): 
        requete = """ select m.contenu from memoires as m join agents as a on a.id = m.agent_id where a.nom ilike %s; """
        self.curseur.execute( requete , ( f"%{nom}%", ) ) 
        resultat = self.curseur.fetchall()
        return resultat
        
    def rechercher_memoire_par_id(self , memoire_id):
        requete = """ select id , agent_id , contenu from memoires where id = %s; """
        self.curseur.execute(requete , (memoire_id,))
        resultat = self.curseur.fetchone() 
        return resultat
    def modifier_memoire(self , contenu , memoire_id ): 
        requete = """ update memoires set  contenu = %s where id = %s; """
        self.curseur.execute(requete , (  contenu , memoire_id )) 
        if self.curseur.rowcount == 1:
              self.connexion.commit() 
              return True
        else:
            return False
    def supprimer_memoire(self , memoire_id):
        requete = """ Delete from memoires where id = %s """
        self.curseur.execute(requete , (memoire_id,))
        if self.curseur.rowcount ==1:
            self.connexion.commit()
            return True
        return False
        
        
  
#print(memoire.rechercher("SQL"))
memoire = Memoire()
#resultat = memoire.rechercher_memoire_par_id(2)
resultat = memoire.rechercher("Bob" , "docker")
print(resultat)
memoire.fermer()