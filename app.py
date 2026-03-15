"""
Application Flask - Calculateur de Cycle Frigorifique
Développée par Christian Lucas
Version Flask pour déploiement sur serveur mutualisé (O2switch)
"""
import os
from flask import Flask, render_template, request, jsonify, session
from calculator import (
    FLUIDES, calculer_cycle, convertir_temperature_pression,
    calculer_rendement_volumetrique_suggere, calculer_valeurs_catalogue,
    calculer_kcat, calculer_proprietes_saturation, calculer_proprietes_deux_phases,
    generer_diagramme_ph
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'calcflu-secret-key-change-in-production')

# Configuration
app.config['SESSION_TYPE'] = 'filesystem'


def get_data():
    """Lit les données de la requête (GET params, form-encoded ou JSON)"""
    if request.method == 'GET':
        return request.args.to_dict()
    if request.is_json:
        return request.get_json() or {}
    return request.form.to_dict()


def get_default_session():
    """Retourne les valeurs par défaut de la session"""
    return {
        'fluide': 'R134a',
        'to_evaporation': None,
        'po_evaporation': None,
        'tc_condensation': None,
        'pk_condensation': None,
        'surchauffe_utile': 5.0,
        'echauffement_sup': 0.0,
        'sous_refroid_cond': 5.0,
        'refroidissement_sup': 0.0,
        'rendement_vol': 0.85,
        'rendement_isen': 0.76,
        'type_metrique': 'Puissance frigorifique utile',
        'valeur_metrique': 0.0,
        'resultats': None,
        # Onglet Compresseur
        'fluide_catalogue': 'R134a',
        'tevap_catalogue': -10.0,
        'tcond_catalogue': 45.0,
        'surchauffe_catalogue': 0.0,
        'sous_ref_catalogue': 0.0,
        'rendement_vol_catalogue': 0.78,
        'h1_catalogue': None,
        'h4_catalogue': None,
        'v1_catalogue': None,
        'kcat': None,
        'puissance_catalogue': None,
        'puissance_choisie': 0.0,
        # Onglet Calculateur
        'calc_resultats': None
    }


def init_session():
    """Initialise la session avec les valeurs par défaut si nécessaire"""
    defaults = get_default_session()
    for key, value in defaults.items():
        if key not in session:
            session[key] = value


@app.before_request
def before_request():
    """Initialiser la session avant chaque requête"""
    init_session()


# ==================== ROUTES PAGES ====================

@app.route('/')
def index():
    """Page d'accueil - Landing page avec lien vers Streamlit"""
    return render_template('landing.html')


@app.route('/parametres')
def parametres():
    """Calculateur - Onglet Paramètres"""
    return render_template('parametres.html',
                         fluides=FLUIDES,
                         active_tab='parametres')


@app.route('/compresseur')
def compresseur():
    """Page Choix de compresseur"""
    return render_template('compresseur.html',
                         fluides=FLUIDES,
                         active_tab='compresseur')


@app.route('/calculateur')
def calculateur():
    """Page Calculateur de propriétés"""
    return render_template('calculateur.html',
                         fluides=FLUIDES,
                         active_tab='calculateur')


@app.route('/diagramme')
def diagramme():
    """Page Diagramme P-h"""
    return render_template('diagramme.html',
                         fluides=FLUIDES,
                         active_tab='diagramme')


# ==================== API ENDPOINTS ====================

@app.route('/api/convertir-tp', methods=['GET', 'POST'])
def api_convertir_tp():
    """API pour convertir température <-> pression"""
    data = get_data()
    fluide = data.get('fluide', session.get('fluide', 'R134a'))
    temperature = data.get('temperature')
    pression = data.get('pression')
    type_point = data.get('type_point', 'evaporation')

    # Convertir en float si nécessaire
    if temperature is not None and temperature != '':
        try:
            temperature = float(temperature)
        except:
            temperature = None
    else:
        temperature = None

    if pression is not None and pression != '':
        try:
            pression = float(pression)
        except:
            pression = None
    else:
        pression = None

    result = convertir_temperature_pression(fluide, temperature, pression, type_point)

    # Calculer le rendement volumétrique suggéré
    if result['success']:
        po = result['pression'] if type_point == 'evaporation' else session.get('po_evaporation')
        pk = result['pression'] if type_point == 'condensation' else session.get('pk_condensation')
        if po and pk:
            result['rendement_vol_suggere'] = calculer_rendement_volumetrique_suggere(po, pk)

    return jsonify(result)


@app.route('/api/calculer-cycle', methods=['GET', 'POST'])
def api_calculer_cycle():
    """API pour calculer le cycle frigorifique complet"""
    data = get_data()

    # Extraire les données du formulaire
    fluide = data.get('fluide', 'R134a')
    to = data.get('to_evaporation')
    po = data.get('po_evaporation')
    tc = data.get('tc_condensation')
    pk = data.get('pk_condensation')
    surchauffe_utile = data.get('surchauffe_utile', 5.0)
    echauffement_sup = data.get('echauffement_sup', 0.0)
    sous_refroid_cond = data.get('sous_refroid_cond', 5.0)
    refroidissement_sup = data.get('refroidissement_sup', 0.0)
    rendement_vol = data.get('rendement_vol', 0.85)
    rendement_isen = data.get('rendement_isen', 0.76)
    type_metrique = data.get('type_metrique', 'Puissance frigorifique utile')
    valeur_metrique = data.get('valeur_metrique', 0.0)

    # Convertir en float
    def to_float(val):
        if val is None or val == '':
            return None
        try:
            return float(val)
        except:
            return None

    to = to_float(to)
    po = to_float(po)
    tc = to_float(tc)
    pk = to_float(pk)
    surchauffe_utile = to_float(surchauffe_utile) or 5.0
    echauffement_sup = to_float(echauffement_sup) or 0.0
    sous_refroid_cond = to_float(sous_refroid_cond) or 5.0
    refroidissement_sup = to_float(refroidissement_sup) or 0.0
    rendement_vol = to_float(rendement_vol) or 0.85
    rendement_isen = to_float(rendement_isen) or 0.76
    valeur_metrique = to_float(valeur_metrique) or 0.0

    # Calculer le cycle
    result = calculer_cycle(
        fluide, to, po, tc, pk,
        surchauffe_utile, echauffement_sup,
        sous_refroid_cond, refroidissement_sup,
        rendement_vol, rendement_isen,
        type_metrique, valeur_metrique
    )

    # Sauvegarder en session si succès
    if result.get('success'):
        session['resultats'] = result
        session['fluide'] = fluide
        session['to_evaporation'] = to
        session['po_evaporation'] = po
        session['tc_condensation'] = tc
        session['pk_condensation'] = pk
        session['surchauffe_utile'] = surchauffe_utile
        session['echauffement_sup'] = echauffement_sup
        session['sous_refroid_cond'] = sous_refroid_cond
        session['refroidissement_sup'] = refroidissement_sup
        session['rendement_vol'] = rendement_vol
        session['rendement_isen'] = rendement_isen
        session['type_metrique'] = type_metrique
        session['valeur_metrique'] = valeur_metrique
        session.modified = True

    return jsonify(result)


@app.route('/api/effacer-cycle', methods=['GET', 'POST'])
def api_effacer_cycle():
    """API pour effacer les résultats du cycle"""
    defaults = get_default_session()
    keys_to_reset = [
        'to_evaporation', 'po_evaporation', 'tc_condensation', 'pk_condensation',
        'echauffement_sup', 'refroidissement_sup', 'valeur_metrique', 'resultats'
    ]
    for key in keys_to_reset:
        session[key] = defaults.get(key)

    session['rendement_vol'] = 0.85
    session['rendement_isen'] = 0.76
    session['surchauffe_utile'] = 5.0
    session['sous_refroid_cond'] = 5.0
    session.modified = True

    return jsonify({'success': True})


@app.route('/api/session', methods=['GET'])
def api_get_session():
    """API pour récupérer l'état de la session"""
    return jsonify(dict(session))


@app.route('/api/calculer-catalogue', methods=['GET', 'POST'])
def api_calculer_catalogue():
    """API pour calculer les valeurs catalogue"""
    data = get_data()

    fluide = data.get('fluide', 'R134a')
    t_evap = float(data.get('t_evap', -10.0))
    t_cond = float(data.get('t_cond', 45.0))
    surchauffe = float(data.get('surchauffe', 0.0))
    sous_ref = float(data.get('sous_refroidissement', 0.0))

    result = calculer_valeurs_catalogue(fluide, t_evap, t_cond, surchauffe, sous_ref)

    if result.get('success'):
        session['h1_catalogue'] = result['h1_prime']
        session['h4_catalogue'] = result['h4_prime']
        session['v1_catalogue'] = result['v1_prime']
        session['rendement_vol_catalogue'] = result['rendement_vol_suggere']
        session.modified = True

    return jsonify(result)


@app.route('/api/effacer-compresseur', methods=['GET', 'POST'])
def api_effacer_compresseur():
    """API pour effacer les données de l'onglet compresseur"""
    for key in ['h1_catalogue', 'h4_catalogue', 'v1_catalogue', 'kcat',
                'puissance_catalogue', 'puissance_choisie',
                'tevap_catalogue', 'tcond_catalogue', 'surchauffe_catalogue',
                'sous_ref_catalogue']:
        session.pop(key, None)
    session['rendement_vol_catalogue'] = 0.78
    session.modified = True
    return jsonify({'success': True})


@app.route('/api/calculer-kcat', methods=['GET', 'POST'])
def api_calculer_kcat():
    """API pour calculer le coefficient Kcat"""
    data = get_data()

    # Vérifier que les résultats du cycle existent
    resultats = session.get('resultats')
    if not resultats or not resultats.get('success'):
        return jsonify({'success': False, 'error': "Calculez d'abord le cycle"})

    # Vérifier que les valeurs catalogue existent
    h1_cat = session.get('h1_catalogue')
    h4_cat = session.get('h4_catalogue')
    v1_cat = session.get('v1_catalogue')
    if h1_cat is None or h4_cat is None or v1_cat is None:
        return jsonify({'success': False, 'error': "Calculez d'abord les valeurs catalogue"})

    # Récupérer les valeurs du cycle
    points = resultats['points']
    perf = resultats['performance']

    h5 = points['5']['H']
    h4 = points['4']['H']
    v1 = points['1']['V']
    rend_vol = session.get('rendement_vol', 0.85)
    puissance_frigo = perf.get('puissance_frigorifique', 0)
    rend_vol_cat = float(data.get('rendement_vol_catalogue', session.get('rendement_vol_catalogue', 0.78)))

    result = calculer_kcat(h5, h4, v1, rend_vol, h1_cat, h4_cat, v1_cat, rend_vol_cat, puissance_frigo)

    if result.get('success'):
        session['kcat'] = result['kcat']
        session['puissance_catalogue'] = result['puissance_catalogue']
        session.modified = True

    return jsonify(result)


@app.route('/api/calculer-proprietes', methods=['GET', 'POST'])
def api_calculer_proprietes():
    """API pour calculer les propriétés thermodynamiques"""
    data = get_data()

    fluide = data.get('fluide', 'R134a')
    type_calcul = data.get('type_calcul', 'saturation')
    type_courbe = data.get('type_courbe', 'rosee')

    # Récupérer les valeurs
    def to_float_or_none(val):
        if val is None or val == '':
            return None
        try:
            return float(val)
        except:
            return None

    T = to_float_or_none(data.get('T'))
    P = to_float_or_none(data.get('P'))
    h = to_float_or_none(data.get('h'))
    s = to_float_or_none(data.get('s'))
    v = to_float_or_none(data.get('v'))
    X = to_float_or_none(data.get('X'))

    if type_calcul == 'saturation':
        result = calculer_proprietes_saturation(fluide, type_courbe, T=T, P=P, h=h, s=s, v=v)
    else:
        result = calculer_proprietes_deux_phases(fluide, T=T, P=P, h=h, s=s, v=v, X=X)

    if result.get('success'):
        session['calc_resultats'] = result
        session.modified = True

    return jsonify(result)


@app.route('/api/effacer-proprietes', methods=['GET', 'POST'])
def api_effacer_proprietes():
    """API pour effacer les résultats du calculateur"""
    session['calc_resultats'] = None
    session.modified = True
    return jsonify({'success': True})


@app.route('/api/generer-diagramme', methods=['GET', 'POST'])
def api_generer_diagramme():
    """API pour générer le diagramme P-h"""
    data = get_data()

    fluide = data.get('fluide', session.get('fluide', 'R134a'))
    inclure_cycle = data.get('inclure_cycle', True)

    # Récupérer les points du cycle si disponibles et demandés
    points_cycle = None
    if inclure_cycle:
        resultats = session.get('resultats')
        if resultats and resultats.get('success'):
            points_cycle = resultats.get('points')

    result = generer_diagramme_ph(fluide, points_cycle)

    return jsonify(result)


# ==================== DIAGNOSTIC ====================

@app.route('/api/diagnostic')
def api_diagnostic():
    """Route de diagnostic pour vérifier CoolProp sur le serveur"""
    import sys
    result = {
        'python_version': sys.version,
        'tests': {}
    }
    try:
        from CoolProp.CoolProp import PropsSI
        import CoolProp
        result['coolprop_version'] = CoolProp.__version__

        fluides_test = {
            'R134a': 'R134a',
            'R410A': 'R410A',
            'R32': 'R32',
            'R513A': 'R513A.mix',
            'R449A': 'R449A.mix',
        }
        for nom, fluide in fluides_test.items():
            row = {}
            for q in [0, 1]:
                try:
                    p = PropsSI('P', 'T', 263.15, 'Q', q, fluide)
                    row[f'Q={q}'] = f'{p/1e5:.3f} bar'
                except Exception as e:
                    row[f'Q={q}'] = f'ERR: {str(e)[:80]}'
            # Test conversion via calculator
            try:
                from calculator import convertir_temperature_pression
                r = convertir_temperature_pression(nom, temperature=-10, pression=None, type_point='evaporation')
                row['api'] = f'{r["pression"]:.3f} bar' if r['success'] else f'ECHEC: {r["error"]}'
            except Exception as e:
                row['api'] = f'EXCEPTION: {str(e)[:80]}'
            result['tests'][nom] = row
    except Exception as e:
        result['coolprop_import_error'] = str(e)

    return jsonify(result)


# ==================== MAIN ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
