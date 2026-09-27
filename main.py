from fastapi import FastAPI ,HTTPException , Depends
from pydantic import BaseModel
from   unbenannt9 import Memoire

def fournir_memoire():
    memoire = Memoire()
    try:
        yield memoire # yiel permet de donner la memoire á l'endpoint et mettre lafonction sur pause
    finally: 
        memoire.fermer()

app = FastAPI()
class Message(BaseModel):
    message: str
    nom: str
    

@app.post("/message")
def recevoir_message( message: Message):
    
    return {"message": message.message , "nom" : message.nom}

class MemoireResponse(BaseModel):
    id : int 
    agent_id : int 
    contenu: str 

@app.get("/memoire/{memoire_id}" , response_model = MemoireResponse) 
def obtenir_memoire( memoire_id : int , memoire : Memoire = Depends( fournir_memoire) ):
    resultat = memoire.rechercher_memoire_par_id(memoire_id)
    if resultat is None:
        raise HTTPException( status_code = 404 , detail = "Memoire introuvable") 
    return { "id" : resultat[0] , "agent_id" : resultat[1]  , "contenu": resultat[2] } 

class Message1(BaseModel):
    contenu : str 
    nom : str
@app.post("/message/" , status_code = 201 , response_model = MemoireResponse)

def ajouter_contenu( message : Message1 , memoire : Memoire = Depends(fournir_memoire) ):
    
     resultat = memoire.ajouter( message.contenu , message.nom ) 
     if resultat is False:
         raise HTTPException( status_code = 404 , detail = "Cet agent n'existe pas")
     return { "id" : resultat[0] , "agent_id" : resultat[1]  , "contenu": resultat[2] }     
class modificationmemoire(BaseModel):
    contenu: str
         
@app.put("/memoires/{memoire_id}")   
def modifier_memoire(memoire_id: int ,modifier: modificationmemoire, memoire: Memoire = Depends(fournir_memoire) ) :
  resultat =   memoire.modifier_memoire(modifier.contenu, memoire_id) 
  
  if resultat is False:
      raise HTTPException( statut_code = 404 , detail=  "Mémoire introuvable")
  return {"message" : "Memoire modifié avec succès"}

@app.delete("/memoires/{memoire_id}")
def supprimer__la_memoire(memoire_id : int , memoire : Memoire = Depends(fournir_memoire) ):
    resultat =  memoire.supprimer_memoire(memoire_id)
    if  resultat is False:
        raise HTTPException( statuts_code = 404 , detail = "Mémoire introuvable")
    return {"message": " mémoire suprimé avec succès"}    