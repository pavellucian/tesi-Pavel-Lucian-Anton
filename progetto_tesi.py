import pandas as pd
import psycopg2
import sys

#connesione al DB
def connect_DB():
    try:
        global conn
        conn = psycopg2.connect(database="terzodb",
                                user = "postgres",
                                host = "localhost",
                                password = "admin",
                                port = 5432)
        global curr
        curr = conn.cursor()
        print("Connessione al database effettuata")
    except:
        print("Errore durante la connessione al databse")
        sys.exit()
        
#funzione per la creazione del DB
def create_DB():
    try:
        con = psycopg2.connect(user = "postgres",
                                host = "localhost",
                                password = "admin",
                                port = 5432)
        con.autocommit = True
        cur = con.cursor()
        cur.execute("""CREATE DATABASE terzodb;""")
        print("Creazione Database effettuata")
        cur.close()
        con.close()
    except psycopg2.errors.DuplicateDatabase:
        print("Database già creato")
    except:
        print("Errore creazione DB")
        sys.exit()

    #connesione al DB appena creato
    connect_DB()

    #creazione tabella Opera
    try:
        curr.execute("""CREATE TABLE Opera(
                     Titolo VARCHAR(124) PRIMARY KEy,
                     Autore VARCHAR(50) NOT NULL
                     );
        """)
        conn.commit()
        print("Creata tabella Opera")
    except psycopg2.errors.DuplicateTable:
        print("Tabella Opera già creata")
        curr.execute("ROLLBACK")
        conn.commit()
    except:
        print("Errore creazione tabella Opera")
        sys.exit()

    #creazione tabella Atto
    try:
        curr.execute("""CREATE TABLE Atto(
                     ID SERIAL PRIMARY KEY,
                     Descrizione Varchar(50) NOT NULL,
                     Opera VARCHAR(124) NOT NULL REFERENCES Opera(Titolo)
                     );
        """)
        conn.commit()
        print("Creata tabella Atto")
    except psycopg2.errors.DuplicateTable:
        print("Tabella Atto già creata")
        curr.execute("ROLLBACK")
        conn.commit()
    except:
        print("Errore creazione tabella Atto")
        sys.exit()

    #creazione tabella Scena
    try:
        curr.execute("""CREATE TABLE Scena(
                     ID SERIAL PRIMARY KEY,
                     Descrizione Varchar(50) NOT NULL,
                     Atto INTEGER NOT NULL REFERENCES Atto(ID)
                     );
        """)
        conn.commit()
        print("Creata tabella Scena")
    except psycopg2.errors.DuplicateTable:
        print("Tabella Scena già creata")
        curr.execute("ROLLBACK")
        conn.commit()
    except:
        print("Errore creazione tabella Scena")
        sys.exit()

    #creazione tabella Logica
    try:
        curr.execute("""CREATE TABLE Logica(
                     Nome VARCHAR(50) PRIMARY KEY,
                     Descrizione VARCHAR(50) NOT NULL
                     );
        """)
        conn.commit()
        print("Creata tabella Logica")
    except psycopg2.errors.DuplicateTable:
        print("Tabella Logica già creata")
        curr.execute("ROLLBACK")
        conn.commit()
    except:
        print("Errore creazione tabella Logica")
        sys.exit()

    #creazione tabella Dialogo
    try:
        curr.execute("""CREATE TABLE Dialogo(
                     ID SERIAL PRIMARY KEY,
                     Speaker VARCHAR(50) NOT NULL,
                     Destinatario VARCHAR(50),
                     Adjuncts VARCHAR(50) [3],
                     Words VARCHAR(100) [20],
                     Scena INTEGER NOT NULL REFERENCES Scena(ID),
                     Logica VARCHAR(50) NOT NULL REFERENCES Logica(Nome)
                     );
        """)
        conn.commit()
        print("Creata tabella Dialogo")
    except psycopg2.errors.DuplicateTable:
        print("Tabella Dialogo già creata")
        curr.execute("ROLLBACK")
        conn.commit()
    except:
        print("Errore creazione tabella Dialogo")
        sys.exit()
    curr.close()
    conn.close()
    input("Premere INVIO per continuare")

#metodo per l'inserimento di un'opera
def insert_opera(titolo,autore):
    if titolo=='': titolo='NULL'
    else: titolo="'"+titolo+"'"
    if autore=='': autore='NULL'
    else: autore="'"+autore+"'"
    try:
        curr.execute("""INSERT INTO Opera VALUES ({0},{1})""".format(titolo,autore))
        conn.commit()
        print("Opera ({0}, {1}) inserita con successo".format(titolo,autore))
    except psycopg2.errors.UniqueViolation:
        print("ERRORE: Opera ({0}, {1}) già presente nel database".format(titolo,autore))
        curr.execute("ROLLBACK")
        conn.commit()
    except psycopg2.errors.NotNullViolation:
        print("ERRORE: Valori null non ammessi")
        curr.execute("ROLLBACK")
        conn.commit()
    input("Premere INVIO per continuare\n")

#metodo per l'inserimento di un'atto
def insert_atto(descrizione,opera):
    if descrizione=='': descrizione='NULL'
    else: descrizione="'"+descrizione+"'"
    if opera=='': opera='NULL'
    else: opera="'"+opera+"'"
    cont='s'
    curr.execute("""SELECT ID FROM Atto
                    WHERE Descrizione={0} AND Opera={1}""".format(descrizione,opera))
    id=str(curr.fetchall())
    if id!="[]":
        print("ATTENZIONE: atto ({0}) già presente per l'opera ({1}),\
vuoi continuare lo stesso? (s/n)".format(descrizione,opera))
        cont=input()
    if cont=='s':
        try:
            curr.execute("""INSERT INTO Atto(Descrizione,Opera)
                            VALUES ({0},{1})""".format(descrizione,opera))
            conn.commit()
            print("Atto ({0}, {1}) inserito con successo".format(descrizione,opera))
        except psycopg2.errors.ForeignKeyViolation:
            print("ERRORE: Opera ({0}) non presente nel database,\
inserire prima l'opera".format(opera))
            curr.execute("ROLLBACK")
            conn.commit()
        except psycopg2.errors.NotNullViolation:
            print("ERRORE: Valori null non ammessi")
            curr.execute("ROLLBACK")
            conn.commit()
        input("Premere INVIO per continuare\n")

#metodo per l'inserimento di una scena
def insert_scena(descrizione,atto):
    if descrizione=='': descrizione='NULL'
    else: descrizione="'"+descrizione+"'"
    if atto=='': atto='NULL'
    else: atto="'"+atto+"'"
    cont='s'
    curr.execute("""SELECT ID FROM Scena
                    WHERE Descrizione={0} AND Atto={1}""".format(descrizione,atto))
    id=str(curr.fetchall())
    if id!="[]":
        print("ATTENZIONE: scena ({0}) già presente per l'atto con id ({1}),\
vuoi continuare lo stesso? (s/n)".format(descrizione,atto))
        cont=input()
    if cont=='s':
        try:
            curr.execute("""INSERT INTO Scena(Descrizione,Atto)
                            VALUES ({0},{1})""".format(descrizione,atto))
            conn.commit()
            print("Scena ({0}, {1}) inserita con successo".format(descrizione,atto))
        except psycopg2.errors.ForeignKeyViolation:
            print("ERRORE: Atto con id {0} non presente nel database,\
inserire prima l'atto".format(atto))
            curr.execute("ROLLBACK")
            conn.commit()
        except psycopg2.errors.NotNullViolation:
            print("ERRORE: Valori null non ammessi")
            curr.execute("ROLLBACK")
            conn.commit()
        input("Premere INVIO per continuare\n")

#metodo per l'inserimento di una logica
def insert_logica(nome,descrizione):
    if nome=='': nome='NULL'
    else: nome="'"+nome+"'"
    if descrizione=='': descrizione='NULL'
    else: descrizione="'"+descrizione+"'"
    try:
        curr.execute("""INSERT INTO Logica
                        VALUES ({0},{1})""".format(nome,descrizione))
        conn.commit()
        print("Logica ({0}, {1}) inserita con successo".format(nome,descrizione))
    except psycopg2.errors.UniqueViolation:
        print("ERRORE: Logica ({0},{1}) già presente nel database\
".format(nome,descrizione))
        curr.execute("ROLLBACK")
        conn.commit()
    except psycopg2.errors.NotNullViolation:
        print("ERRORE: Valori null non ammessi")
        curr.execute("ROLLBACK")
        conn.commit()
    input("Premere INVIO per continuare\n")

#metodo per l'inserimento di un dialogo
def insert_dialogo(speaker,destinatario,adjuncts,words,id_scena,logica):
    if speaker=='': speaker='NULL'
    else: speaker="'"+speaker+"'"
    if destinatario=='': destinatario='NULL'
    else: destinatario="'"+destinatario+"'"
    if adjuncts=='': adjuncts='NULL'
    else: adjuncts="'"+adjuncts+"'"
    if words=='': words='NULL'
    else: words="'"+words+"'"
    if id_scena=='': id_scena='NULL'
    else: id_scena="'"+id_scena+"'"
    if logica=='': logica='NULL'
    else: logica="'"+logica+"'"
    cont='s'
    curr.execute("""SELECT ID FROM Dialogo
                    WHERE Speaker={0} AND Destinatario={1} AND Adjuncts={2}
                          AND Words={3} AND Scena={4} AND Logica={5}
                 """.format(speaker,destinatario,adjuncts,words,id_scena,logica))
    id=str(curr.fetchall())
    if id!="[]":
        print("ATTENZIONE: dialogo già presente con questi dati\nSpeaker={0}\n\
Destinatario={1}\nAdjuncts={2}\nWords={3}\nID_Scena={4}\nLogica={5}\n \
vuoi continuare lo stesso? \
(s/n)".format(speaker,destinatario,adjuncts,words,id_scena,logica))
        cont=input()
    if cont=='s':   
        try:
            curr.execute("""INSERT INTO Dialogo(Speaker,Destinatario,Adjuncts,Words,Scena,Logica)
                            VALUES ({0},{1},{2},{3},{4},{5})
                         """.format(speaker,destinatario,adjuncts,words,id_scena,logica))
            conn.commit()
            print("Dialogo con questi dati\nSpeaker={0}\nDestinatario={1}\nAdjuncts={2}\n\
Words={3}\nID_Scena={4}\nLogica={5}\ninserito con \
successo".format(speaker,destinatario,adjuncts,words,id_scena,logica))
        except psycopg2.errors.ForeignKeyViolation:
            print("ERRORE: Scena ({0}) o logica ({1}) non presente nel database, \
inserirli prima di inserire il dialogo".format(id_scena,logica))
            curr.execute("ROLLBACK")
            conn.commit()
        except psycopg2.errors.NotNullViolation:
            print("ERRORE: Valori null inseriti dove non ammessi")
            curr.execute("ROLLBACK")
            conn.commit()
        input("Premere INVIO per continuare\n")

#metodo per l'inserimento manuale di un'opera
def manual_insert_opera():
    titolo1=input("Inserire nome dell'opera\n")
    autore1=input("Inserire autore dell'opera\n")
    insert_opera(titolo1,autore1)

#metodo per l'inserimento manuale di un'atto
def manual_insert_atto():
    descrizione1=input("Inserire descrizione dell'atto\n")
    opera1=input("Inserire il titolo dell'opera a cui si riferisce\n")
    insert_atto(descrizione1,opera1)
    
#metodo per l'inserimento manuale di una scena
def manual_insert_scena():
    descrizione1=input("Inserire descrizione della scena\n")
    atto1=input("Inserire l'ID dell'atto a cui si riferisce\n")
    insert_scena(descrizione1,atto1)
    
#metodo per l'inserimento manuale di una logica
def manual_insert_logica():
    nome1=input("Inserire il nome della logica\n")
    descrizione1=input("Inserire la descrizione della logica\n")
    insert_logica(nome1,descrizione1)

#metodo per l'inserimento manuale di un dialogo
def manual_insert_dialogo():
    speaker1=input("Inserire il nome dello speaker del dialogo\n")
    destinatario1=input("Inserire il nome del destinatario del dialogo\
(Opzioanale)\n")
    i=0
    while (i not in[1,2,3]):
        try:
            i=int(input("Inserire il numero di adjuncts che si vuole inserire\
(min 1, max 3)\n"))
        except:
            print("ERRORE: Inserire un numero compreso tra 1 e 3")
    adjuncts1="{"
    for j in range(i):
        if j>0 : adjuncts1 = adjuncts1+","
        adjuncts1=adjuncts1+input("Inserire adjunct\n")
    adjuncts1=adjuncts1+"}"
    
    i=0
    while (i not in range(1,21)):
        try:
            i=int(input("Inserire il numero di words che si vuole inserire\
(min 1, max 20)\n"))
        except:
            print("ERRORE: Inserire un numero compreso tra 1 e 20")
    words1="{"
    for j in range(i):
        if j>0: words1=words1+","
        words1=words1+input("Inserire word\n")
    words1=words1+"}"
    
    scena1=input("Inserire ID della scena relativa al dialogo\n")
    logica1=input("Inserire nome della logica del dialogo\n")
    
    insert_dialogo(speaker1,destinatario1,adjuncts1,words1,scena1,logica1)
    
#metodo per gestire l'inserimento manuale dei dati
def manual_insert():
    #connesione al DB
    connect_DB()
        
    fine=False
    while not(fine):
        print("Inserire il numero di relativo a ciò che si vuole inserire")
        print("1. Opera")
        print("2. Atto")
        print("3. Scena")
        print("4. Logica")
        print("5. Dialogo")
        print("")
        print("6. Per tornare indietro")
        try:
            tab = int(input())
        except:
            print("ERRORE: Inserire un numero compreso tra 1 e 6")
            continue
        if tab==1: manual_insert_opera()
        elif tab==2: manual_insert_atto()
        elif tab==3: manual_insert_scena()
        elif tab==4: manual_insert_logica()
        elif tab==5: manual_insert_dialogo()
        elif tab==6: fine=True
        else: print("ATTENZIONE! Inserire un numero compreso tra 1 e 6")
    curr.close()
    conn.close()

#inserimento dati da folgio excel
def insert_from_excel():
    #connesione al DB
    connect_DB()
    
    ok=False
    while not(ok):
        file=input("Inserire il nome del file\n")
        foglio=input("Inserire il nome del foglio all'interno del foglio elettronico\n")
        try:
            df=pd.read_excel(file,sheet_name=foglio)
            ok=True
        except FileNotFoundError:
            print("ERRORE: File non trovato")
        except ValueError:
            print("ERRORE: Foglio non trovato")

    titolo=input("Inserire titolo dell'opera\n")
    autore=input("Inserire autore dell'opera\n")
    insert_opera(titolo,autore)
    
    print("Inserimento LOGICA")
    riga=int(input("Inserire il numero della prima riga in cui si trovano le logiche,\
non contando le righe totalemente vuote\n"))
    colonna=int(input("Inserire il numero della colonna in cui si trovano le logiche,\
non contando le colonne totalemente vuote\n"))
    n=int(input("Inserire il numero di logiche presenti\n"))
    for i in range(n):
        logic=df.iat[riga+i,colonna]
        tokens=logic.split(":")
        insert_logica(tokens[0].strip(),tokens[1].strip())

    riga=df.shape[0]
    colonna=df.shape[1]
    att=0
    fine=False
    while not(fine):
        if "ACT " in str(df.iat[att+1,0]):
            fine=True
        att+=1

    id_atto=''
    id_scena=''

    while att<riga:
        if "ACT " in str(df.iat[att,0]):
            atto=df.iat[att,0]
            insert_atto(atto,titolo)
            att+=1
            curr.execute("""SELECT ID FROM Atto WHERE Descrizione='{0}' AND Opera='{1}'
                        """.format(atto,titolo))
            id_atto=str(curr.fetchone())
            id_atto=id_atto.strip('(')
            id_atto=id_atto.strip(',)')
        if str(df.iat[att,1])!='nan':
            insert_scena(df.iat[att,1],id_atto)
            curr.execute("""SELECT ID FROM Scena WHERE Descrizione='{0}' AND Atto='{1}'
                         """.format(df.iat[att,1],id_atto))
            id_scena=str(curr.fetchone())
            id_scena=id_scena.strip('(')
            id_scena=id_scena.strip(',)')
        if str(df.iat[att,2])!='nan':
            speaker=''
            destinatario=''
            adjuncts=''
            words=''
            logica=''
            for col in range(2,colonna):
                if col==2:
                    tp=str(df.iat[att,col])
                    if tp!='nan':
                        speaker=tp
                elif col==3:
                    tp=str(df.iat[att,col])
                    if tp!='nan':
                        destinatario=tp
                elif col==4:
                    tp=str(df.iat[att,col])
                    if tp!='nan':
                        logica=tp.lower()
                elif col==6:
                    tp=str(df.iat[att,col])
                    if tp!='nan':
                        adjuncts='{'+tp
                elif col==7:
                    tp=str(df.iat[att,col])
                    if tp!='nan':
                        if adjuncts!='':
                            adjuncts=adjuncts+','+tp
                        else:
                            adjuncts='{'+tp
                elif col==8:
                    tp=str(df.iat[att,col])
                    if tp!='nan':
                        if adjuncts!='':
                            adjuncts=adjuncts+','+tp
                        else:
                            adjuncts='{'+tp
                elif (col>=9 and col<colonna):
                    tp=str(df.iat[att,col])
                    if tp!='nan':
                        if words!='':
                            words=words+','+tp
                        else:
                            words='{'+tp
            if adjuncts!='':
                adjuncts=adjuncts+'}'
            if words!='':
                words=words+'}'
            words=words.replace("'","''")
            insert_dialogo(speaker,destinatario,adjuncts,words,id_scena,logica)
        att+=1

    curr.close()
    conn.close()

#stampa opere
def stampa_opere():
    stop=False
    while not(stop):
        print("Inserire il numero di ciò che si vuole stampare")
        print("1. Stampa tutte le opere raggruppate per autore")
        print("2. Stampa le opere di un solo autore scelto")
        print("")
        print("3. Per tornare indietro")
        try:
            op=int(input())
        except:
            print("ERRORE: Inserire un numero compreso tra 1 e 3")
        if op==1:
            curr.execute("""SELECT * FROM Opera ORDER BY Autore""")
            print("TITOLO  AUTORE")
            n=0
            for record in curr:
                print(record)
                n=+1
            conn.commit()
            print("Numero record: {0}".format(n))
            input("Premere INVIO per continuare")
        elif op==2:
            print("Inserire il nome dell'autore")
            autore=str(input())
            curr.execute("""SELECT * FROM Opera WHERE Autore='{0}'""".format(autore))
            print("TITOLO  AUTORE")
            n=0
            for record in curr:
                print(record)
                n+=1
            conn.commit()
            print("Numero record: {0}".format(n))
            input("Premere INVIO per continuare")
        elif op==3:
            stop=True
        else:
            print("ATTENZIONE! Inserire un numero compreso tra 1 e 3")

#stampa atti
def stampa_atti():
    stop=False
    while not(stop):
        print("Inserire il numero di ciò che si vuole stampare")
        print("1. Stampa tutte gli atti raggruppati per opera")
        print("2. Stampa gli atti di una sola opera scelta")
        print("")
        print("3. Per tornare indietro")
        try:
            op=int(input())
        except:
            print("ERRORE: Inserire un numero compreso tra 1 e 3")
            continue
        if op==1:
            curr.execute("""SELECT * FROM Atto ORDER BY Opera""")
            print("ID  DESCRIZIONE  OPERA")
            n=0
            for record in curr:
                print(record)
                n+=1
            conn.commit()
            print("Numero record: {0}".format(n))
            input("Premere INVIO per continuare")
        elif op==2:
            print("Inserire il nome dell'opera")
            opera=str(input())
            curr.execute("""SELECT * FROM Atto WHERE opera='{0}'""".format(opera))
            print("ID  DESCRIZIONE  OPERA")
            n=0
            for record in curr:
                print(record)
                n+=1
            conn.commit()
            print("Numero record: {0}".format(n))
            input("Premere INVIO per continuare")
        elif op==3:
            stop=True
        else:
            print("ATTENZIONE! Inserire un numero compreso tra 1 e 3")

#stampa scene
def stampa_scene():
    stop=False
    while not(stop):
        print("Inserire il numero di ciò che si vuole stampare")
        print("1. Stampa tutte le scene raggruppati per atto,opera")
        print("2. Stampa le scene di un atto")
        print("3. Stampa le scene di un opera")
        print("")
        print("4. Per tornare indietro")
        try:
            op=int(input())
        except:
            print("ERRORE: Inserire un numero compreso tra 1 e 4")
            continue
        if op==1:
            curr.execute("""SELECT Scena.id,Scena.descrizione,Atto.descrizione,
                                   Atto.opera
                            FROM Scena LEFT JOIN Atto ON Scena.atto=Atto.id
                            ORDER BY Atto.opera,Atto.descrizione""")
            print("ID  DESCRIZIONE_SCENA DESCRIZIONE_ATTO  OPERA")
            n=0
            for record in curr:
                print(record)
                n+=1
            conn.commit()
            print("Numero record: {0}".format(n))
            input("Premere INVIO per continuare")
        elif op==2:
            print("Inserire l'ID dell'atto")
            try:
                id_atto=int(input())
            except:
                print("ERRORE")
                continue
            curr.execute("""SELECT Scena.id,Scena.descrizione,Scena.atto,
                                   Atto.descrizione,Atto.opera
                            FROM Scena LEFT JOIN Atto ON Scena.atto=Atto.id
                            WHERE Scena.atto='{0}'""".format(id_atto))
            print("ID  DESCRIZIONE_SCENA ID_ATTO DESCRIZIONE_ATTO  OPERA")
            n=0
            for record in curr:
                print(record)
                n+=1
            conn.commit()
            print("Numero record: {0}".format(n))
            input("Premere INVIO per continuare")
        elif op==3:
            print("Inserire titolo dell'opera")
            opera=str(input())
            curr.execute("""SELECT Scena.id,Scena.descrizione,Atto.descrizione,
                            Atto.opera
                            FROM Scena LEFT JOIN Atto ON Scena.atto=Atto.id
                            WHERE Atto.opera='{0}'
                            ORDER BY Atto.descrizione""".format(opera))
            print("ID  DESCRIZIONE_SCENA ID_ATTO DESCRIZIONE_ATTO  OPERA")
            n=0
            for record in curr:
                print(record)
                n+=1
            conn.commit()
            print("Numero record: {0}".format(n))
            input("Premere INVIO per continuare")
        elif op==4:
            stop=True
        else:
            print("ATTENZIONE! Inserire un numero compreso tra 1 e 4")

#stampa logiche
def stampa_logiche():
    curr.execute("""SELECT * FROM Logica""")
    print("NOME  DESCRIZIONE")
    n=0
    for record in curr:
        print(record)
        n+=1
    conn.commit()
    print("Numero record: {0}".format(n))
    input("Premere INVIO per continuare")

#stampa dialoghi
def stampa_dialoghi():
    stop=False
    while not(stop):
        print("Inserire il numero di ciò che si vuole stampare")
        print("1. Stampa tutti i dialoghi raggruppati per scena,atto,opera")
        print("2. Stampa i dialoghi relativi au uno speaker")
        print("3. Stampa i dialoghi relativi ad un destinatario")
        print("4. Stampa i dialoghi relativi ad una scena")
        print("5. Stampa i dialoghi relativi ad un atto")
        print("6. Stampa i dialoghi relativi ad un'opera")
        print("")
        print("7. Per tornare indietro")
        try:
            op=int(input())
        except:
            print("ERRORE: Inserire un numero compreso tra 1 e 7")
            continue
        if op==1:
            curr.execute("""SELECT Dialogo.id,Dialogo.speaker,Dialogo.destinatario,
                                   Dialogo.adjuncts,Dialogo.words,Dialogo.logica,
                                   Scena.descrizione,Atto.descrizione,Atto.opera
                            FROM Dialogo LEFT JOIN Scena on Dialogo.scena=Scena.id
                                         LEFT JOIN Atto on Scena.atto=Atto.id
                            ORDER BY Atto.Opera,Atto.descrizione,Scena.descrizione,
                                     Dialogo.id""")
            print("ID  SPEAKER  DESTINATARIO  ADJUNCTS  WORDS  LOGICA  SCENA  ATTO\
OPERA")
            n=0
            for record in curr:
                print(record)
                n+=1
            conn.commit()
            print("Numero record: {0}".format(n))
            input("Premere INVIO per continuare")
        elif op==2:
            print("Inserire il nome dello speaker")
            speaker=str(input())
            curr.execute("""SELECT Dialogo.id,Dialogo.speaker,Dialogo.destinatario,
                                   Dialogo.adjuncts,Dialogo.words,Dialogo.logica,
                                   Scena.descrizione,Atto.descrizione,Atto.opera
                            FROM Dialogo LEFT JOIN Scena on Dialogo.scena=Scena.id
                                         LEFT JOIN Atto on Scena.atto=Atto.id
                            WHERE Dialogo.speaker='{0}'
                            ORDER BY Atto.Opera,Atto.descrizione,Scena.descrizione,
                                  Dialogo.id""".format(speaker))
            print("ID  SPEAKER  DESTINATARIO  ADJUNCTS  WORDS  LOGICA  SCENA  ATTO\
OPERA")
            n=0
            for record in curr:
                print(record)
                n+=1
            conn.commit()
            print("Numero record: {0}".format(n))
            input("Premere INVIO per continuare")
        elif op==3:
            print("Inserire il nome del destinatario")
            destinatario=str(input())
            curr.execute("""SELECT Dialogo.id,Dialogo.speaker,Dialogo.destinatario,
                                   Dialogo.adjuncts,Dialogo.words,Dialogo.logica,
                                   Scena.descrizione,Atto.descrizione,Atto.opera
                            FROM Dialogo LEFT JOIN Scena on Dialogo.scena=Scena.id
                                         LEFT JOIN Atto on Scena.atto=Atto.id
                            WHERE Dialogo.destinatario='{0}'
                            ORDER BY Atto.Opera,Atto.descrizione,Scena.descrizione,
                                     Dialogo.id""".format(destinatario))
            print("ID  SPEAKER  DESTINATARIO  ADJUNCTS  WORDS  LOGICA  SCENA  ATTO\
OPERA")
            n=0
            for record in curr:
                print(record)
                n+=1
            conn.commit()
            print("Numero record: {0}".format(n))
            input("Premere INVIO per continuare")
        elif op==4:
            print("Inserire l'id della scena")
            try:
                id_scena=int(input())
            except:
                print("ERRORE")
                continue
            curr.execute("""SELECT Dialogo.id,Dialogo.speaker,Dialogo.destinatario,
                                   Dialogo.adjuncts,Dialogo.words,Dialogo.logica,
                                   Scena.id,Scena.descrizione,Atto.descrizione,
                                   Atto.opera
                            FROM Dialogo LEFT JOIN Scena on Dialogo.scena=Scena.id
                                         LEFT JOIN Atto on Scena.atto=Atto.id
                            WHERE Scena.id='{0}'
                            ORDER BY Atto.Opera,Atto.descrizione,Scena.descrizione,
                                     Dialogo.id""".format(id_scena))
            print("ID  SPEAKER  DESTINATARIO  ADJUNCTS  WORDS  LOGICA ID_SCENA\
SCENA  ATTO  OPERA")
            n=0
            for record in curr:
                print(record)
                n+=1
            conn.commit()
            print("Numero record: {0}".format(n))
            input("Premere INVIO per continuare")
        elif op==5:
            print("Inserire l'id dell'atto")
            try:
                id_atto=int(input())
            except:
                print("ERRORE")
                continue
            curr.execute("""SELECT Dialogo.id,Dialogo.speaker,Dialogo.destinatario,
                                   Dialogo.adjuncts,Dialogo.words,Dialogo.logica,
                                   Scena.descrizione,Atto.id,Atto.descrizione,
                                   Atto.opera
                            FROM Dialogo LEFT JOIN Scena on Dialogo.scena=Scena.id
                                         LEFT JOIN Atto on Scena.atto=Atto.id
                            WHERE Atto.id='{0}'
                            ORDER BY Atto.Opera,Atto.descrizione,Scena.descrizione,
                                     Dialogo.id""".format(id_atto))
            print("ID  SPEAKER  DESTINATARIO  ADJUNCTS  WORDS  LOGICA  SCENA\
ID_ATTO  ATTO  OPERA")
            n=0
            for record in curr:
                print(record)
                n+=1
            conn.commit()
            print("Numero record: {0}".format(n))
            input("Premere INVIO per continuare")
        elif op==6:
            print("Inserire il titolo dell'opera")
            opera=str(input())
            curr.execute("""SELECT Dialogo.id,Dialogo.speaker,Dialogo.destinatario,
                                   Dialogo.adjuncts,Dialogo.words,Dialogo.logica,
                                   Scena.descrizione,Atto.descrizione,Atto.opera
                            FROM Dialogo LEFT JOIN Scena on Dialogo.scena=Scena.id
                                         LEFT JOIN Atto on Scena.atto=Atto.id
                            WHERE Atto.opera='{0}'
                            ORDER BY Atto.Opera,Atto.descrizione,Scena.descrizione,
                                     Dialogo.id""".format(opera))
            print("ID  SPEAKER  DESTINATARIO  ADJUNCTS  WORDS  LOGICA  SCENA\
ATTO  OPERA")
            n=0
            for record in curr:
                print(record)
                n+=1
            conn.commit()
            print("Numero record: {0}".format(n))
            input("Premere INVIO per continuare")
        elif op==7:
            stop=True
        else:
            print("ATTENZIONE! Inserire un numero compreso tra 1 e 7")

#stampa dati
def visualize_data():
    #connesione al DB
    connect_DB()
    
    stop=False
    while not(stop):
        print("Inserire il numero di ciò che si vuole stampare")
        print("1. Stampa opere")
        print("2. Stampa atti")
        print("3. Stampa scene")
        print("4. Stampa logiche")
        print("5. Stampa dialoghi")
        print("")
        print("6. Per tornare indietro")
        try:
            op=int(input())
        except:
            print("ERRORE: Inserire un numero compreso tra 1 e 6")
            continue
        if op==1:
            stampa_opere()
        elif op==2:
            stampa_atti()
        elif op==3:
            stampa_scene()
        elif op==4:
            stampa_logiche()
        elif op==5:
            stampa_dialoghi()
        elif op==6: 
            stop=True
        else:
            print("ATTENZIONE! Inserire un numero compreso tra 1 e 6")
    curr.close()
    conn.close()

if __name__ == "__main__":
    stop=False
    #loop che permette all'utente di eseguire più operazioni ogni volta che esegue
    #il programma
    while not(stop):
        print("Inserire il numero dell'operazione che si vuole sseguire")
        print("1. Creazione database")
        print("2. Inserimento dati da foglio excel")
        print("3. Inserimento manuale dei dati")
        print("4. Stampa dati")
        print("")
        print("5. Per uscire dal programma")
        try:
            op = int(input())
        except:
            print("ERRORE: Inserire un numero compreso tra 1 e 5")
            continue
        if op==1:
            create_DB()         #creazione DB
        elif op==2:
            insert_from_excel() #inserimento dati da foglio excel
        elif op==3:
            manual_insert()     #inserimento manuale
        elif op==4:
            visualize_data()    #stampa dati
        elif op==5:
            stop=True
        else: print("ATTENZIONE! Inserire un numero compreso tra 1 e 5")
