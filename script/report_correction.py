#! /usr/bin/env python3

import os
import glob
import json
import shutil
import logging
import argparse
import pandas as pd
from redmail import gmail
from datetime import date

class Correction_report:

  def __init__(self):
    self.elenco = []
    self.list_missing_both = []


  def create_student_folder(self):
    try:
      all_files = sorted(glob.glob(os.path.join(report_folder, "/*.pdf")))
      for filein in all_files:
        try:
          tok = filein.split('/')[-1].split('_')
          new_folder = f'{report_folder}/{tok[0]}_{tok[1]}'
          file_name = '_'.join(tok)
          if not os.path.exists(new_folder): os.mkdir(new_folder)

          os.rename(f"{filein}", f"{new_folder}/{file_name}")
        except Exception as e:
          logging.error(f"[create_student_folder][IN] Error: {e}")

      for file in os.listdir(report_folder):
        os.rename(f'{report_folder}/' + file, f'{report_folder}/' + file.lower())

      self.elenco = os.listdir(report_folder)
    except Exception as e:
      logging.error(f"[create_student_folder] Error: {e}")



  def dataframe_creation(self):
    try:
      for i, corso in enumerate(course_name):
        corso_folder = f'{report_folder}/{corso}'
        if not os.path.exists(corso_folder): os.mkdir(corso_folder)

        corso_list = pd.read_csv(f'{matInfo}/informatica/{corso}_list/lista_studenti.csv', sep = ',')
        corso_list = corso_list.apply(lambda x: x.astype(str).str.lower()).replace(' ', '', regex=True)
        corso_list['people'] = corso_list.Cognome + '_' + corso_list.Nome
        corso_people = corso_list['people'].tolist()#.sort()
        corso_people.sort()
        for folder_name in self.elenco:
          try:
            if folder_name in corso_people: shutil.move(os.path.join(report_folder, folder_name), corso_folder)
          except Exception as e:
            logging.error(f"[dataframe_creation][IN] Error: {e}")

        corso_list.set_index('people', inplace = True)
        corso_list = corso_list.sort_index()
        corso_list = corso_list.rename(columns={'Indirizzo email':'email'})

        people_dict = dict(zip(corso_list.index, corso_list.email))

        folder_list = [name for name in os.listdir(corso_folder) if os.path.isdir(os.path.join(corso_folder, name))] 
        missing_student = list(set(corso_people) - set(folder_list))

        df_missing = corso_list.loc[corso_list.index.isin(missing_student)]
        self.list_missing_both.append(df_missing)

        df_mark = pd.DataFrame(folder_list, columns=['cognome_nome'])
        df_mark['email'] = df_mark.cognome_nome.map(people_dict)

        df_mark[['cognome', 'nome']] = df_mark['cognome_nome'].str.split('_', expand=True)
        df_mark.set_index('cognome_nome', inplace = True)

        df_mark[['cognome', 'nome']] = df_mark[['cognome', 'nome']].apply(lambda x: x.astype(str).str.capitalize())
        df_mark[f'valutazione_progetto_{relazione_n}'] = ''

        df_mark = df_mark[['cognome','nome','email',f'valutazione_progetto_{relazione_n}']]
        df_mark.to_csv(f'{corso_folder}/valutazione_progetto_{relazione_n}.csv', sep = ';', index=False)

    except Exception as e:
      logging.error(f"[dataframe_creation] Error: {e}")


  def send_warning(self, username, pwd):
    logging.info(f'Number of missing report: {len(self.list_missing_both[0])}, {len(self.list_missing_both[1])}')

    df_missing_both = pd.concat(self.list_missing_both)
    df_missing_both = df_missing_both.rename(columns={'Indirizzo email':'email'})

    for i, row in df_missing_both.iterrows():
      with open(f'{text_folder}/warning_text.txt') as f:
        body = eval(f'f"""{f.read()}"""')

      gmail.username = username
      gmail.password = pwd

      try:
        logging.info(f"[send_warning] Sending mail to {row.email}")
        gmail.send( subject=f"Mancata ricezione della relazione {relazione_n} - Corso Matematica-Informatica",
                    receivers=['federico.bellisardi2@unibo.it'],
                    text=body)
      except Exception as e:
        logging.error(f"[send_warning] Error in sending mail to {row.email}")
      break

  def send_mark(self,username,pwd):
    valutazioni_path = os.path.join(matInfo, 'informatica','relazioni')
    for i, corso in enumerate(course_name):
      # df_valutazioni = pd.read_csv(f'{valutazioni_path}/{relazione_n}_relazione/valutazioni_definitive_{corso}.csv', sep = ';')
      df_valutazioni = pd.read_csv(f'{valutazioni_path}/valutazioni_definitive_biotec_test.csv', sep = ';')

      for i, row in df_valutazioni.iterrows():
        if row.valutazione_progetto_I == 'insufficiente':
          with open(f'{text_folder}/bad_mark.txt') as f:
            body = eval(f'f"""{f.read()}"""')

        else:
          with open(f'{text_folder}/good_mark.txt', 'r') as f:
            body = eval(f'f"""{f.read()}"""')


        gmail.username = username
        gmail.password = pwd

        try:
          logging.info(f"[send_mark] Sending mail to {row.mail}")
          gmail.send( subject=f"Valutazione {relazione_n} progetto - Corso Matematica-Informatica",
                      receivers=['federico.bellisardi2@unibo.it'],
                      text=body)
        except Exception as e:
          logging.error(f"[send_mark] Error in sending mail to {row.mail}")
        exit()
        break


  # for i, corso in enumerate(course_name):
  #   df_mark = pd.read_csv(f'{report_folder}/valutazioni_definitive_{corso}_test.csv', sep=';')
  #   df_mark = df_mark.apply(lambda x: x.astype(str).str.lower())
  #   df_mark['people'] = df_mark.Cognome + '_' + df_mark.Nome
  #   df_mark.set_index('people', inplace = True)
  #   df_mark = df_mark.sort_index()
  #   df_mail_list = pd.read_csv(f'{matInfo}/{corso}_list/lista_studenti.csv', sep = ',')
  #   df_mail_list = df_mail_list.apply(lambda x: x.astype(str).str.lower()).replace(' ','', regex=True)
  #   df_mail_list['people'] = df_mail_list.Cognome + '_' + df_mail_list.Nome
  #   df_mail_list.set_index('people', inplace = True)
  #   df_mail_list = df_mail_list.sort_index()
  #   df_mail_list = df_mail_list.rename(columns={'Indirizzo email':'email'})

  #   people_dict = dict(zip(df_mail_list.index, df_mail_list.email))

  #   df_mark['mail'] = df_mark.index.map(people_dict)
  #   df_mark = df_mark[['Cognome','Nome','mail','valutazione_progetto_{relazione_n}']]
  #   print(df_mark)
  #   # df_mark.to_csv(f'{report_folder}/valutazioni_definitive_{corso}_test2.csv', sep = ';', index=False)



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-c', '--cfg', help='json config file', required=True)
  parser.add_argument('-sf', '--sf', help='create students folder', action='store_true', default=True)
  parser.add_argument('-df', '--df', help='marks dataframe creation', action='store_true', default=True)
  parser.add_argument('-w', '--warning', help='send warning mail to missing students', action='store_true', default=False)
  parser.add_argument('-ms', '--ms', help='send mail to students with marks', action='store_true', default=False)

  args = parser.parse_args()
  
  
  with open(args.cfg, encoding="utf8") as cfgfile:
    config = json.loads(cfgfile.read())

  relazione_n = config['relazione_n']
  matInfo = config['matInfo']
  course_name = ['biotec', 'ctf']

  username = config["username"]
  pwd = config["pwd"]


  report_folder = os.path.join(matInfo, 'informatica','relazioni', f'{relazione_n}_relazione_test')
  text_folder = os.path.join(matInfo, 'informatica','relazioni', 'text_folder')

  logging.basicConfig(level=logging.DEBUG, filename=f"{report_folder}/logfile.log", filemode="a+",format="%(asctime)-15s %(levelname)-8s %(message)s")

  c = Correction_report()
  if args.sf:       student_folder = c.create_student_folder()
  if args.df:       create_df = c.dataframe_creation()
  if args.warning:  warning_mail = c.send_warning(username, pwd)
  if args.ms:       mark_send = c.send_mark(username, pwd)



