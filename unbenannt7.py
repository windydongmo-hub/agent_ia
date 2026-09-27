# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 18:15:10 2026

@author: windy
"""

import json
from openai import OpenAI
import os
import unbenannt9


# ============================================================
# CONFIGURATION DE L'API
# ============================================================

cle = os.environ["OPENROUTER_API_KEY"]




# ============================================================
# CLASSE AGENT
# ============================================================

class Agent:

    def __init__(self, nom, modele):

        self.nom = nom
        self.modele = modele

        self.memoire = unbenannt9.Memoire(self.nom)
        
        self.conversation = [] 
        self.client =  OpenAI(
    api_key=cle,
    base_url="https://openrouter.ai/api/v1"
)

        self.outils = {

            "rechercher": {

                "fonction": self.chercher,

                "description": "Recherche une information",

                "parameters": {
                    "type": "object",

                    "properties": {

                        "mot": {
                            "type": "string",
                            
                            "description": "Le mot ou le nom à rechercher dans la mémoire"
                        }
                    },

                    "required": ["mot"]
                }
            },


            "retenir": {

                "fonction": self.recevoir_et_retenir,

                "description": "Retient une information importante",

                "parameters": {
                    "type": "object",

                    "properties": {

                        "message": {
                            "type": "string",
                            "description": "Le message important à mémoriser"
                        }
                    },

                    "required": ["message"]
                }
            }
        }


    # ========================================================
    # TRANSFORMER NOS OUTILS POUR LE LLM
    # ========================================================

    def obtenir_outils_pour_llm(self):

        outils_llm = []

        for nom in self.outils:

            outil = self.outils[nom]

            outil_llm = {

                "type": "function",

                "function": {

                    "name": nom,

                    "description": outil["description"],

                    "parameters": outil["parameters"]
                }
            }

            outils_llm.append(outil_llm)

        return outils_llm


    # ========================================================
    # EXECUTER UN OUTIL DEMANDER PAR LE LLM
    # ========================================================

    def execution_outil(self, appel):

      nom_outil = appel.function.name
      if nom_outil not in self.outils:
            return f"L'outil {nom_outil}  ne se trouve pas dans le dictionnaire"
      try:
        argument = json.loads(
            appel.function.arguments
        )
        
        outil = self.outils[nom_outil]
         
        valeur_obligatoire = outil["parameters"]["required"]
        parametre = outil["parameters"]["properties"]
        correspondance = {"string": str ,
                         "integer": int ,
                         "boolean" : bool ,
                         "object" : dict ,
                         "array" : list,}
        for nom_parametre in valeur_obligatoire:
            valeur = argument.get(nom_parametre)
            if valeur is None:
                return f"le parametre {nom_parametre} est obligatoire "
            type_attendu = parametre[nom_parametre]["type"]
            type_python = correspondance[type_attendu]
            if not isinstance(valeur, type_python):
              return (
                f"le parametre {nom_parametre} doit etre du type "
                f"{type_attendu}")
            
        fonction = outil["fonction"]
    

        resultat = fonction(**argument)
       

        return resultat
      except Exception as e:
            return f"Erreur lors de l'execution de {e}"

    # ========================================================
    # BOUCLE PRINCIPALE DE L'AGENT
    # ========================================================

    def executer(self):
        

        while True:

            # ------------------------------------------------
            # 1. On envoie les messages au LLM
            # ------------------------------------------------

            response = self.client.chat.completions.create(

                model= self.modele,

                messages=self.conversation,

                tools=self.obtenir_outils_pour_llm()
            )

           #print(response)
            # ------------------------------------------------
            # 2. On récupère le message du LLM
            # ------------------------------------------------
            
            message = response.choices[0].message


            # ------------------------------------------------
            # 3. Est-ce que le LLM demande un outil ?
            # ------------------------------------------------

            if message.tool_calls:

                # On ajoute la réponse du LLM
                # à l'historique

                self.conversation.append(message)


                # ------------------------------------------------
                # 4. On parcourt les appels d'outils
                # ------------------------------------------------
                
                for appel in message.tool_calls:

                    resultat = self.execution_outil(appel)


                    # ------------------------------------------------
                    # 5. On construit la réponse de l'outil
                    # ------------------------------------------------

                    message_tool = {

                        "role": "tool",# le tool veux dire: ce message contient le resultat d'un outil

                        "tool_call_id": appel.id,

                        "content": str(resultat)
                    }


                    # ------------------------------------------------
                    # 6. On ajoute le résultat à l'historique
                    # ------------------------------------------------

                    self.conversation.append(message_tool)


            # ------------------------------------------------
            # 7. Le LLM n'a plus besoin d'outil
            # ------------------------------------------------

            else:
                self.conversation.append(message)

                return message.content


    # ========================================================
    # MÉMOIRE
    # ========================================================

    def recevoir(self, message):

        self.memoire.ajouter(message)


    def lire_memoire(self):

        return self.memoire.afficher()


    def chercher(self, mot):

        return self.memoire.rechercher(mot)


    def effacer_memoire(self):

        self.memoire.effacer()


    def se_souvenir(self, information):

        resultat = self.memoire.rechercher(information)

        return len(resultat) > 0
    def fermer_ligne(self):
          self.memoire.fermer()
       
           
       

    

    # ========================================================
    # MÉMOIRE IMPORTANTE
    # ========================================================

    def est_important(self, message):

        mot_important = [
            "client",
            "urgent",
            "important",
            "projet"
        ]

        for mot in mot_important:

           if mot.lower() in message.lower():

                return True

        return False


    def recevoir_et_retenir(self, message):
        print("MESSAGE REÇU PAR PYTHON :", repr(message))
        if self.est_important(message):
         
           return self.recevoir(message)


    # ========================================================
    # CONVERSATION
    # ========================================================

    def discuter(self , message):

        self.conversation.append( {
            "role" : "user",
            "content" : message }) 


    def afficher_conversation(self):

        return self.conversation


    def effacer_conversation(self):

        self.conversation.clear()


    def finir_conversation(self):

        for message in self.conversation:

            self.recevoir_et_retenir(message)

        self.effacer_conversation()


    # ========================================================
    # ANCIEN SYSTÈME DE DÉTECTION
    # ========================================================

    """def choisir_action(self, message):

        action = []

        liste1 = [
            "cherche",
            "recherche",
            "trouve",
            "retrouve"
        ]

        liste2 = [
            "important",
            "urgent",
            "urgence"
        ]

        for k in liste1:

            if k.lower() in message.lower():

                action.append("rechercher")


        for k in liste2:

            if k.lower() in message.lower():

                action.append("retenir")


        if len(action) == 0:

            action.append("repondre")


        return action"""


    """def analyser_message(self, message):

        action1 = self.choisir_action(message)

        for l in action1:

            if l == "rechercher":

                mot = self.extrai_donnees(message)

                return {
                    "action": action1,
                    "mot": mot
                }"""


    """def extrai_donnees(self, message):

        liste_nom = [
            "Bob",
            "Alvine",
            "Alice",
            "Marine",
            "Franck"
        ]

        for nom in liste_nom:

            if nom.lower() in message.lower().split():

                return nom.lower()"""


    """def executer_action(self, analyse, message):

        resultat = []

        for k in analyse["action"]:

            if k.lower() == "rechercher":

                resultat.append(
                    self.chercher(analyse["mot"])
                )


            elif k.lower() == "retenir":

                resultat.append(
                    self.recevoir_et_retenir(message)
                )


            elif k.lower() == "repondre":

                resultat.append(
                    "Je dois répondre à ce message"
                )


        return resultat """


    """def traiter_message(self, message):

        analyse = self.analyser_message(message)

        return self.executer_action(
            analyse,
            message
        )"""


    # ========================================================
    # AFFICHER LES OUTILS
    # ========================================================

    def dictionaire(self):

        for nom in self.outils:

            outil = self.outils[nom]

            print("nom :", nom)

            print("outil :", outil)


# ============================================================
# CRÉATION DES AGENTS
# ============================================================

agent1 = Agent("Alice", "nvidia/nemotron-3-ultra-550b-a55b:free")

agent2 = Agent("Bob", "nvidia/nemotron-3-ultra-550b-a55b:free")


# ============================================================
# MESSAGE DE DÉPART
# ============================================================




# ============================================================
# LANCEMENT DE L'AGENT
# ============================================================
#agent1.discuter("recherche alice dans ma memoire ")
agent2.discuter("Recherche Bob dans ma base de donnés et retient que ses donnés sont précieu ")
#agent1.discuter("Recherche Alice dans la base de données et retient que cette cela est important")
resultat = agent2.executer()
print(resultat)
#print(resultat)
#print(agent2.lire_memoire())
agent2.fermer_ligne()
agent1.fermer_ligne()
