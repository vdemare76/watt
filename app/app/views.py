from flask import flash, render_template, redirect, url_for, request
from flask_appbuilder import ModelView, BaseView, expose, has_access, action
from flask_appbuilder.fieldwidgets import Select2Widget
from flask_appbuilder.models.sqla.interface import SQLAInterface
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from flask_appbuilder.fieldwidgets import Select2AJAXWidget, Select2SlaveAJAXWidget
from flask_appbuilder.fields import AJAXSelectField
from wtforms import validators

from .import appbuilder, db
from .models import AnnoAccademico, CorsoDiStudio, AttivitaDidattica, Docente, Aula, Offerta, \
                    LogisticaDocente, Modulo, Giorno, Slot, Orario, OrarioTestata
from flask.templating import render_template
from .util import inizializzaDb, svuotaDb
from .solver import AlgoritmoCompleto

class AnniAccademiciView(ModelView):
    datamodel = SQLAInterface(AnnoAccademico)
    label_columns = {"anno":"Anno accademico",
                     "anno_esteso":"Anno accademico esteso"}
    list_columns = ["anno", 
                    "anno_esteso"]
        
class SlotView(ModelView):
    datamodel = SQLAInterface(Slot)
    label_columns = {"descrizione":"Descrizione"}
    list_columns = ["descrizione"]
    
class GiorniView(ModelView):
    datamodel = SQLAInterface(Giorno)
    label_columns = {"descrizione":"Descrizione"}
    list_columns = ["descrizione"]
    
class CorsiDiStudioView(ModelView):
    datamodel = SQLAInterface(CorsoDiStudio)
    label_columns = {"codice":"Codice CdS",
                     "descrizione":"Descrizione",
                     "cfu":"Cfu",
                     "durata_legale":"Durata legale"}
    list_columns = ["codice", 
                    "descrizione", 
                    "cfu", 
                    "durata_legale"]

class AttivitaDidatticheView(ModelView):
    datamodel = SQLAInterface(AttivitaDidattica)
    label_columns = {"codice":"Codice AD",
                     "Descrizione":"Descrizione",
                     "cfu":"Cfu"}
    list_columns = ["codice", 
                    "descrizione", 
                    "cfu"]
    
class AuleView(ModelView):
    datamodel = SQLAInterface(Aula)
    label_columns = {"codice":"Codice aula",
                     "descrizione":"Descrizione",
                     "capienza":"Capienza",
                     "tipo_aula":"Tipo aula"}
    list_columns = ["codice", 
                    "descrizione", 
                    "capienza",
                    "tipo_aula"]

class DocentiView(ModelView):
    datamodel = SQLAInterface(Docente)
    label_columns = {"codice_fiscale":"Codice fiscale",
                     "cognome":"Cognome",
                     "nome":"Nome"}
    list_columns = ["codice_fiscale", 
                    "cognome", 
                    "nome"]
    search_filters = ["codice_fiscale", 
                    "cognome", 
                    "nome"] 
    
class OffertaView(ModelView):
    datamodel = SQLAInterface(Offerta)
    label_columns = {"anno_accademico.anno_esteso":"Anno accademico",
                     "corso_di_studio.descrizione":"Corso di studio",
                     "attivita_didattica.descrizione":"Attività didattica",
                     "docente.cognome":"Cognome docente",
                     "docente.nome":"Nome docente",
                     "anno_di_corso":"Anno di corso",
                     "semestre":"Semestre",
                     "max_studenti":"Numerosità studenti"}
    list_columns = ["anno_accademico.anno_esteso",
                    "corso_di_studio.descrizione",
                    "attivita_didattica.descrizione",
                    "docente.cognome","docente.nome",
                    "anno_di_corso",
                    "semestre",
                    "max_studenti"]
    
class ModuliView(ModelView):
    datamodel = SQLAInterface(Modulo)
    label_columns = {"codice":"Codice modulo",
                     "descrizione":"Descrizione",
                     "offerta.anno_accademico":"A.A. Offerta",
                     "offerta.corso_di_studio":"C.d.S Offerta",
                     "offerta.attivita_didattica":"AD Offerta",
                     "tipo_aula":"Tipo aula",
                     "docente.cognome":"Cognome docente",
                     "docente.nome":"Nome docente",
                     "numero_sessioni":"Numero di sessioni",
                     "durata_sessioni":"Durata sessioni",
                     "max_studenti":"Numerosità massima studenti"}
    list_columns = ["codice",
                    "descrizione",
                    "offerta.anno_accademico",
                    "offerta.corso_di_studio",
                    "offerta.attivita_didattica",
                    "tipo_aula",
                    "docente.cognome",
                    "docente.nome",
                    "numero_sessioni",
                    "durata_sessioni",
                    "max_studenti"]
    order_columns = ["codice",
                    "descrizione",
                    "tipo_aula",
                    "docente.cognome",
                    "docente.nome",
                    "numero_sessioni",
                    "durata_sessioni",
                    "max_studenti"]
    
class LogisticaDocentiView(ModelView):
    datamodel = SQLAInterface(LogisticaDocente)

    label_columns = {"offerta.attivita_didattica":"Offerta",
                     "modulo.descrizione":"Modulo",
                     "slot.descrizione":"Slot",
                     "giorno.descrizione":"Giorno"}
    
    list_columns = ["offerta.attivita_didattica",
                    "modulo.descrizione",
                    "slot.descrizione",
                    "giorno.descrizione"]
       
    add_form_extra_fields = {
         "offerta": AJAXSelectField(
            "Offerta",
            datamodel=datamodel,
            validators=[validators.DataRequired()],
            col_name="offerta",
            widget=Select2AJAXWidget(
                endpoint="/logisticadocentiview/api/column/add/offerta"
            ),
        ),
        'modulo': AJAXSelectField(
            'Modulo',
            datamodel=datamodel,
            validators=[validators.DataRequired()],
            col_name="modulo",
            widget=Select2SlaveAJAXWidget(
                master_id="offerta",
                endpoint="/logisticadocentiview/api/column/add/modulo?_flt_0_offerta_id={{ID}}",
            )
        )
    }
    
    edit_form_extra_fields = add_form_extra_fields 

class OrariGeneratiView(ModelView):
    datamodel = SQLAInterface(OrarioTestata)
    label_columns = {"descrizione":"Descrizione",
                     "anno_accademico.anno_esteso":"Anno Accademico",
                     "semestre":"Semestre",
                     "data_creazione":"Data creazione"}
    list_columns = ["descrizione",
                    "anno_accademico.anno_esteso",
                    "semestre",
                    "data_creazione"]

    @action("cancella", "Cancella", "Delete all Really?", "fa-rocket", single=False)
    def cancella(self, items):
        flash("ECCO")
        return redirect(self.get_redirect())

class UtilitaView(BaseView):
    default_view = 'srv_home'

    @expose('/srv_home/')
    @has_access
    def srv_home(self, name=None):
        return render_template("utilita.html", base_template=appbuilder.base_template, appbuilder=appbuilder)
    
    @expose('/srv_initdb/<target>')
    @has_access
    def srv_util(self, target=None):     
        if target=="initdb":
            if inizializzaDb()==0:
                flash('Inizializzazione del db effettuata correttamente!','success')
            else:    
                flash('Errore nella fase di inizializzazione del db.','error')
        elif target=="emptydb":
            if svuotaDb()==0:
                flash('Db svuotato correttamente!','success')
            else:    
                flash('Errore nella fase di svuotamento del db.','error')
        return redirect(url_for('UtilitaView.srv_home'));

class PreferenzeView(BaseView):
    default_view = 'prf_home'

    @expose('/prf_home/', methods=['GET','POST'])
    @has_access
    def prf_home(self, name=None):
        anni_accademici=db.session.query(AnnoAccademico.id, AnnoAccademico.anno, AnnoAccademico.anno_esteso)\
        .join(Offerta, Offerta.anno_accademico_id==AnnoAccademico.id).distinct()
        semestri=db.session.query(Offerta.semestre).distinct()
        return render_template("preferenze.html", 
                                base_template=appbuilder.base_template, 
                                appbuilder=appbuilder,
                                anni_accademici=anni_accademici, 
                                semestri=semestri)
    
    @expose('/prf_calc/<target>', methods=['GET','POST'])
    @has_access
    def prf_calc(self, target=None):
        if target=="genera_orario" :
            algoritmo=AlgoritmoCompleto()
            algoritmo.genera_orario(request.form.get('aa'),request.form.get('semestre'),request.form.get('txt_desc_orario'))
        return redirect(url_for('PreferenzeView.prf_home'));  
    
class CalendarioView(BaseView):
    default_view = 'cld_home'

    @expose('/cld_home/')
    @has_access
    def cld_home(self, name=None):
        slot=db.session.query(Slot).all()
        orario=db.session.query(Orario).all()
        return render_template("calendario.html", 
                               base_template=appbuilder.base_template, 
                               appbuilder=appbuilder, 
                               slot=slot,
                               orario=orario)

class SchemaSettimanaleView(BaseView):
    default_view = 'wsk_home'

    @expose('/wsk_home/')
    @has_access
    def wsk_home(self, name=None):
        return render_template("week_model.html", 
                               base_template=appbuilder.base_template, 
                               appbuilder=appbuilder)
          
db.create_all()


appbuilder.add_view(SlotView, "Slot", icon="fa-clock-o", category="Tabelle di base")

appbuilder.add_view(GiorniView, "Giorni", icon="fa-calendar-check-o", category="Tabelle di base")

appbuilder.add_separator("Tabelle di base")

appbuilder.add_view(AnniAccademiciView, "Anni Accademici", icon="fa-font", category="Tabelle di base")

appbuilder.add_view(AuleView, "Aule", icon="fa-th", category="Tabelle di base")

appbuilder.add_view(CorsiDiStudioView, "Corsi di Studio", icon="fa-pencil", category="Didattica")

appbuilder.add_view(DocentiView, "Docenti", icon="fa-user-circle", category="Didattica")

appbuilder.add_view(AttivitaDidatticheView, "Attività didattiche", icon="fa-book", category="Didattica")

appbuilder.add_view(OffertaView, "Offerta", icon="fa-university", category="Offerta didattica")

appbuilder.add_view(ModuliView, "Moduli", icon="fa-puzzle-piece", category="Offerta didattica")

appbuilder.add_view(LogisticaDocentiView, "Logistica docenti", icon="fa-hand-o-up", category="Offerta didattica")

appbuilder.add_view(UtilitaView, "Funzioni utilità",  icon="fa-cogs", category="Admin")

appbuilder.add_view(PreferenzeView, "Elaborazione orario",  icon="fa-cogs", category="Admin")

appbuilder.add_view(OrariGeneratiView, "Orari generati",  icon="fa-cogs", category="Admin")

appbuilder.add_view(CalendarioView, "Calendario orario",  icon="fa-cogs", category="Admin")

appbuilder.add_view(SchemaSettimanaleView, "Schema settimanale",  icon="fa-cogs", category="Admin")

