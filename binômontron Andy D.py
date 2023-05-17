# Importation des dépendances requises pour le code
import random
import mysql.connector
from datetime import date

# Connexion à la BDD
mydb = mysql.connector.connect(
  host="localhost",
  port="3307",
  user="root",
  password="example",
  database="apprenants"
)

# Création du curseur qui sert à exécuter les requêtes
mycursor=mydb.cursor()

# Fonctions : 

# Fonction qui fixe la taille de la liste du nombre d'élève par groupe, et qui retourne la liste sous forme d'ID au lieu de noms
def fix_taille(liste,nombre):

  # liste = la liste des élèves; nombre = le nombre d'élève en surplus
  
  # Si nombre est égal à 0, alors il n'y a pas d'élève en surplus, sinon il y a des élèves en surplus
  if nombre==0:
    print("\nNombre d'élève rond, personne n'est sans groupe !")
    reste=False 
  elif nombre>0: 
    print("\nNombre d'élève pas rond, un groupe ne sera pas conforme.")
    reste=True
  return len(liste)-nombre,reste
# Renvoi de la taille conforme au nombre d'élève par groupe et de l'existence de reste ou non.

# Cette fonction sert à créer le projet et l'inscrire dans la BDD
def formation_projet():
  nom_projet=input("Entrez le nom du projet : ")
  date_deb=input("Date de début (AAAA-MM-JJ) : ")
  date_fin=input("Date de fin   (AAAA-MM-JJ) : ")
  # Execution de la requète SQL pour entrer le projet dans la BDD
  mycursor.execute('INSERT INTO projet(libelle,debut,fin) VALUES(%s,%s,%s)' , (nom_projet,date_deb,date_fin))
  # Puis récupération de l'ID du projet créé pour le réutiliser plus tard lors de l'assignation des projets
  mycursor.execute('SELECT id FROM projet WHERE libelle = %s', (nom_projet,))
  projet_id=mycursor.fetchone()[0] 
  mycursor.fetchall()
  return projet_id
# Renvoi de l'id du projet créé

# Cette fonction sert à séparer les élèves en groupes et appelle ensuite la fonction pour les nommer et insérer en BDD
def formation_groupe(liste,nb_pers,ppgroupe,reste):
# liste = liste des élèves, nb_pers = taille liste conforme à ppgroupe
# ppgroupe = nombre de personnes par groupe, reste = existence d'un surplus ou non

  # Création du projet sur lequel les groupes vont travailler, et récupération de l'ID du projet via la fonction précédente
  projet_id=formation_projet()

  # Séparation du groupe en fonction de ppgroupe
  for i in range(0,nb_pers,ppgroupe):
    print("\nGroupe :")
    # Initialisation pour enregistrement des ids du groupe en cours de création dans une liste 
    # afin de les entrer en BDD ensuite
    ids_du_groupe=[]

    # Pour chaque élève du groupe, récupérer et stocker son ID pour l'entrer en BDD plus tard.
    for i2 in range(ppgroupe):
      print(liste[i+i2])
      ids_du_groupe.append(get_id(liste[i+i2]))

    # Création du groupe dans la BDD avec une fonction créée à cet effet
    create_gp_bdd(ids_du_groupe,projet_id)
  
  # S'il existe un surplus, création d'un groupe avec les élèves en surplus, même fonctionnement qu'au dessus
  if reste:
    ids_du_groupe=[]
    print("\nGroupe :")

    for i in range((len(liste)%ppgroupe)):
      print(liste[-(i+1)])
      ids_du_groupe.append(get_id(liste[-(i+1)]))

    create_gp_bdd(ids_du_groupe,projet_id)
      
# Cette fonction sert à nommer et insérer les froupes dans la BDD
def create_gp_bdd(ids,projet_id):
# ids = ID de chaque élève dans le groupe, projet_id = ID du projet du groupe

  nom_groupe=input("Nom du groupe : ")
  # Execution de la requète SQL pour entrer le groupe dans la BDD
  mycursor.execute('INSERT INTO groupe(libelle,date) VALUES(%s,%s)', (nom_groupe, date.today()))
  # Puis récupération de l'ID du groupe créé pour le réutiliser juste après lors de l'assignation des groupes
  mycursor.execute('SELECT id_groupe FROM groupe WHERE libelle = %s', (nom_groupe,))
  groupe_id=mycursor.fetchone()[0]
  mycursor.fetchall()
  # Pour chaque membre du groupe, insertion dans la BDD de l'élève, son groupe, et son projet.
  for id in ids:
    mycursor.execute('INSERT INTO dans_groupe (id_apprenant,id_groupe,id_projet) VALUES (%s,%s,%s)',(id,groupe_id,projet_id))

# Cette fonction sert à récupérer l'ID d'un élève donné
def get_id(el1):
# el1 = liste contenant le nom puis le prénom de l'élève
  
  mycursor.execute("SELECT id FROM apprenant WHERE nom=%s AND prenom=%s",el1.split(" "))
  return mycursor.fetchone()[0]
# Renvoi de l'ID récupéré

# Cette fonction sert à afficher la liste des projets
def afficher_projets():
  
  # Execution de la requète SQL pour récupérer le libellé de chaque projet
  mycursor.execute("SELECT libelle FROM projet")
  print("\nVoici la liste des projets : \n")
  # Affichage de chaque nom de projet
  for i in mycursor:
    print(i[0])

# Cette fonction sert à récupérer la liste des groupes pour un projet donné
def groupes_pour_projet():

  nom_projet=input("\nEntrez le nom du projet : ")
  
  # Attrappe les erreurs au cas où le projet n'existe pas et retour au menu
  try: 
    # Récupération de la liste des groupes du projet donné
    mycursor.execute('SELECT a.nom, a.prenom, g.libelle AS groupe, p.libelle AS projet FROM dans_groupe dg LEFT JOIN apprenant a ON a.id = dg.id_apprenant LEFT JOIN groupe g ON g.id_groupe = dg.id_groupe LEFT JOIN projet p ON p.id = dg.id_projet WHERE p.libelle = %s ORDER BY p.libelle, g.libelle;', (nom_projet,))
    # Récupération du premier élève et de son groupe pour pouvoir comparer le groupe avec les élèves suivants
    # Afin de mettre ensemble et séparer les différents groupes
    first=mycursor.fetchone()
    gp_actuel=first[2]
    print("\nGroupe",gp_actuel,":\n")
    print(first[0]+" "+first[1])
    for x in mycursor:
      if gp_actuel!=x[2]:
        gp_actuel=x[2]
        print("\nGroupe",gp_actuel,":\n")
      print(x[0]+" "+x[1])
  except:
    print("Le projet n'existe pas, retour au menu")

# Initialisation de la variable pour sortir du menu une fois avoir fini d'utiliser le programme
fini=False

while not fini:

  # Création du menu et choix
  choix=int(input("\n1 : Créer des groupes\n2 : Afficher l'email d'un élève donné\n3 : Afficher la liste des projets\n4 : Afficher les groupes pour un projet donné\n5 : Quitter\nChoix : "))
  if choix==1:
  # Choix 1 : Créer des groupes

    # Liste servant à stocker les élèves
    apprenants=[]
    # Execution de la requète SQL pour récupérer la liste d'élèves
    mycursor.execute("SELECT nom, prenom FROM apprenant")

    # Affectation des élèves dans la liste sous forme de chaines de caractère
    for i in mycursor:
        apprenants.append(str(i[0]+" "+i[1]))
    
    # Mélange de la liste pour créer des groupes aléatoires
    random.shuffle(apprenants)

    ppgroupe=int(input("Quel est le nombre de personnes par groupe ? : "))

    # Calcul du nombre de personnes en surplus par rapport au nombre de personnes
    # par groupes et de la taille de la classe, et utilisation de la fonction
    # fix_taille développée lors de sa création
    eleves_restants=len(apprenants)%ppgroupe
    nb_pers,reste=fix_taille(apprenants,eleves_restants)

    # Formation du groupe en fonction de la liste
    formation_groupe(apprenants,nb_pers,ppgroupe,reste)
    
    # Confirmation à la BDD des changements et de la formation des groupes
    mydb.commit()

  if choix==2:
  # Choix 2 : Afficher l'email d'un élève donné

    nom=input("\nEntrez le nom de famille de l'élève : ").upper()
    prénom=input("Entrez le prénom de l'élève : ").capitalize()
    # Execution de la requète SQL pour récupérer l'email de l'élève en question
    mycursor.execute("SELECT mail FROM apprenant WHERE nom=%s AND prenom=%s",(nom,prénom))
    print("l'email de "+nom+" "+prénom+" est : "+mycursor.fetchone()[0])
  if choix==3:
  # Choix 3 : Afficher tous les projets dans la BDD
    afficher_projets()
  if choix==4:
  # Choix 4 : Afficher tous les groupes pour un projet donné
    groupes_pour_projet()
  if choix==5:
  # Affectation de la variable pour indiquer qu'on a fini d'utiliser le programme
    fini=True
  
# Fermeture du curseur et de la base de données
mycursor.close()
mydb.close()