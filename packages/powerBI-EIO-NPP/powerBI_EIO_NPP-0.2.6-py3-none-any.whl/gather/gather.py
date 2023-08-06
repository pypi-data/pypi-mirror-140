from ast import If
import os.path

from pickle import NONE
from SynologyAPI import synology_API
from catbackupAPI import CatbackupAPI_NPP
from PandoraAPI import PandoraFMS_API
from HyperbackupAPI2 import HyperbackupAPI2_NPP
from refresher import refresher
import argparse
import wget

__version__= "0.2.6"
def main(args=None):
    
    parser = argparse.ArgumentParser(description='Serveix per actualitzar dashboard de PowerBI desktop localment.')
    parser.add_argument('--portable-chrome-path', help="La ruta del executable de chrome", default=NONE, metavar="RUTA")
    parser.add_argument('-q', '--quiet', help='Nomes mostra els errors i el missatge de acabada per pantalla.', action="store_false")
    parser.add_argument('-v', '--versio', help='Mostra la versio', action='version', version='refresh-PowerBI v'+__version__)
    args = parser.parse_args(args)

    rutaExcelPandora = "" # ex: C:\\Users\\npujol\\eio.cat\\Eio-sistemes - Documentos\\General\\Drive\\utilitats\\APIs\\powerBI\\excelPandora.xlsx
    rutaExcelSynology = ""# ex: C:\\Users\\npujol\eio.cat\\Eio-sistemes - Documentos\\General\\Drive\\utilitats\\APIs\\powerBI\\excelSynology.xlsx
    rutaJSONSynology = ""# ex: C:\\Users\\npujol\\eio.cat\\Eio-sistemes - Documentos\\General\\Drive\\utilitats\\APIs\\powerBI\\dadesSynology.json
    rutaJSONCatbackup =""# ex: C:\\Users\\npujol\\eio.cat\\Eio-sistemes - Documentos\\General\\Drive\\utilitats\\APIs\\powerBI\\dadesCatbackup.json
    rutaJSONPandora ="" # ex: C:\\Users\\npujol\\eio.cat\\Eio-sistemes - Documentos\\General\\Drive\\utilitats\\APIs\\powerBI\\dadesPandora.json
    rutaJSONHyperbackup2=""# ex: C:\\Users\\npujol\\eio.cat\\Eio-sistemes - Documentos\\General\\Drive\\utilitats\\APIs\\powerBI\\dadesHyperBackup2.json
    rutaJSONLlegenda=""# ex: C:\\Users\\npujol\\eio.cat\\Eio-sistemes - Documentos\General\\Drive\\utilitats\\APIs\\powerBI\\llegendaPowerBI.json
    rutaPBIX=""# ex: C:\\Users\\npujol\\eio.cat\\Eio-sistemes - Documentos\\General\\Drive\\utilitats\\APIs\\powerBI\\apis.pbix

    
    if not(os.path.isfile(rutaJSONLlegenda)):
        wget.download("https://github.com/NilPujolPorta/powerBI-EIO-NPP/blob/master/llegendaPowerBI.json?raw=true", rutaJSONLlegenda)

    if not(args.quiet):
        PandoraFMS_API.main(['-q','-e','-f',rutaExcelPandora,'--json-file',rutaJSONPandora])
        synology_API.main(['-q','-e','--json-file',rutaJSONSynology,'-f',rutaExcelSynology])
        if args.portable_chrome_path != NONE:
            CatbackupAPI_NPP.main(['-q','--json-file',rutaJSONCatbackup,'--portable-chrome-path', args.portable_chrome_path])
            HyperbackupAPI2_NPP.main(['-q','--json-file',rutaJSONHyperbackup2,'--portable-chrome-path', args.portable_chrome_path])
        else:
            CatbackupAPI_NPP.main(['-q','--json-file',rutaJSONCatbackup])
            HyperbackupAPI2_NPP.main(['-q','--json-file',rutaJSONHyperbackup2])
    else:
        PandoraFMS_API.main(['-e','-f',rutaExcelPandora,'--json-file',rutaJSONPandora])
        synology_API.main(['-e','--json-file',rutaJSONSynology,'-f',rutaExcelSynology])
        if args.portable_chrome_path != NONE:
            CatbackupAPI_NPP.main(['--json-file',rutaJSONCatbackup,'--portable-chrome-path', args.portable_chrome_path])
            HyperbackupAPI2_NPP.main(['--json-file',rutaJSONHyperbackup2,'--portable-chrome-path', args.portable_chrome_path])
        else:
            CatbackupAPI_NPP.main(['--json-file',rutaJSONCatbackup])
            HyperbackupAPI2_NPP.main(['--json-file',rutaJSONHyperbackup2])
    try:
        refresher.main(['-f',rutaPBIX])
    except:
        print("Error en refrescar. Assegura't que el fitxer existeix")

if __name__ =='__main__':
    main()