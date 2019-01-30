from django.http import JsonResponse
#import requests

import json
import makEasy
import jsonpickle

#me_folder=u'/home/worksite/PyApp/makEasy/'
me_folder=makEasy.FOLDER+'/'
print('percordo',me_folder)
prj_folder=me_folder+'Projects/'


def new(request):
    if (request.method == "POST" and request.POST['prj_name']):
        prj_name=request.POST['prj_name']
        prj=makEasy.projectLibrary[prj_name]
        prj_path=prj.Path

        # load form structure
        f = open(prj_folder+prj_path+'/form.json', 'r')
        data=json.load(f)
        f.close()

        # load js functions
        f = open(prj_folder+prj_path+'/project.js', 'r')
        prj_script=f.read()
        f.close()

        # load project default data
        f = open(prj_folder+prj_path+'/data.json', 'r')
        prj_data=json.load(f)
        f.close()

        data = dict(prj_name=prj_name,
                    form_data=data["form_data"],
                    prj_script=prj_script,
                    prj_data=prj_data,
                    prj_title=prj.Title)

        return JsonResponse(data)


def getJson(request):
    path=me_folder+request.POST['jsonPath']
    source={}
    f = open(path, 'r')
    source=f.read()
    f.close()
    data= dict(source=source,path=path)
    return  JsonResponse(data)


def createItem(request):
    json_item='{}'
    if request.POST['name']:
        prj_data=json.loads(request.POST['jsonstring'])
        item=makEasy.newItemFromProject(request.POST['name'],prj_data)
        json_item=jsonpickle.encode(item)
    return JsonResponse(dict(item=json_item))


def exportDXF(request):
    dxf=''
    if request.POST['name']:
        data=json.loads(request.POST['jsonstring'])
        item=makEasy.newItemFromProject(request.POST['name'],data['data_form'])
        wf=item.WorkFlow
        for ws in wf:
            if ws.Work.Class=='PlasmaCut':
                dxf=ws.getDXF()
    return JsonResponse(dict(dxf=[dxf]))

def sendOffer(request):

    def data_to_html(data):
        html="<ul>"
        for f in data:
            while len(f)>0:
                d=f.popitem()
                html+="<li>"+d[0]+": "
                if d[1].__class__.__name__=='list':
                    html+=data_to_html(d[1])
                else:
                    html+=str(d[1])
                html+="</li>"
        html+="</ul>"
        return html

    # get parameters
    prj_name=request.POST['prj_name']
    json_prj_data=request.POST['prj_data']
    prj_data=json.loads(json_prj_data)
    json_offer=request.POST['offer']
    offer=json.loads(json_offer)

    #create items
    item=makEasy.newItemFromProject(prj_name,prj_data)
    wf=item.WorkFlow

    #get project data
    prj=makEasy.projectLibrary[prj_name]
    prj_path=prj.Path

    f = open(prj_folder+prj_path+'/form.json', 'r')
    prj_form=json.load(f)
    f.close()

    prj_repr=item.Project.getDataRepr(item.ProjectParameters)

    html=''
    html+="<p>"
    html+="Buongiorno,<br>Vi comunichiamo offerta per la fornitura di:<br><br>"
    html+="Nr "+str(offer['data_form']['quantity'])+" "
    html+=item.Project.Title
    html+=" con le seguenti caratteristiche:<br>"
    html+=data_to_html(prj_repr)
    html+="</p>"
    html+="<p>"
    html+="Sono comprese le seguenti lavorazioni:"
    html+="<ul>"
    for v in range(0,len(offer['data_form']['works'])):
        w=offer['data_form']['works']
        if json.loads(w[v])['selected']=='true':
            html+="<li>"+wf[v].Work.Title+"</li>"
    html+="</ul>"
    html+="</p>"
    html+="<p>"

    result=requests.post(
        "https://api.mailgun.net/v3/carpenteriasoldini.it/messages",
        auth=("api", "key-88b2ca18a8d06347d6f9fd35b7fe8a07"),
        data={"from": "SOLDINI snc - Offerte <info@carpenteriasoldini.it>",
              "to": "produzione@carpenteriasoldini.it",
              "subject": "Offerta",
              "html": html})
    if result.reason=='OK':
        msg="Richiesta inviata con successo"
    else:
        msg="Errore nell'invio della richiesta. Verifica l'indirizzo"

    return JsonResponse(dict(msg=jsonpickle.encode(wf)))
